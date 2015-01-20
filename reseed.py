#!/usr/bin/env python

from bencode import bdecode
import requests
import json
from os import path, listdir, remove
from glob import glob
from collections import namedtuple
from argparse import ArgumentParser

sess = requests.Session()

session_id = ''

e8 = lambda s: s.encode('utf8')
d8 = lambda s: s.decode('utf8')

Response = namedtuple('Response', 'success error arguments tag')

def rpc_call(method, arguments=None, tag=None):
  req = construct_req(method, arguments, tag)
  resp = do_post(req)
  if resp.status_code != 200:
    raise Exception('unexpected status code %d' % resp.status_code)
  j = resp.json()
  if j['result'] == 'success':
    success = True
    error = None
  else:
    success = False
    error = j['result']
  return Response(success=success,
                  error=error,
                  arguments=j.get('arguments', None),
                  tag=j.get('tag', None))

def construct_req(method, arguments, tag):
  req = {'method': method}
  if arguments:
    req['arguments'] = arguments
  if tag:
    req['tag'] = tag
  return json.dumps(req)

url = '' # will be set from command line later

def do_post(req):
  global session_id
  resp = sess.post(url, data=req, headers={'X-Transmission-Session-Id': session_id})
  if resp.status_code == 409:
    session_id = resp.headers['x-transmission-session-id']
    return do_post(req)
  return resp

def torrent_add(filename, download_dir=None, paused=False):
  arguments = {'filename': filename,
               'paused': paused}
  if download_dir:
    arguments['download-dir'] = download_dir
  return rpc_call('torrent-add', arguments)

if __name__ == '__main__':
  parser = ArgumentParser(description='Mass import torrents into Transmission, setting download location automatically')
  parser.add_argument('--torrentdir', '-t', action='append', type=unicode, required=True,
                      help='where to look for .torrent files (can be specified multiple times)')
  parser.add_argument('--datadir', '-d', action='append', type=unicode, required=True,
                      help='where to look for data (can be specified multiple times)')
  parser.add_argument('--url', '-u', default='http://localhost:9091/transmission/rpc',
                      help='URL to Transmission\' RPC API')
  parser.add_argument('--start', action='store_true',
                      help='add torrents in started (non-paused) state (not recommended)')
  cmdline = parser.parse_args()
  url = cmdline.url

  data_loc = {}
  for datadir in cmdline.datadir:
    data_loc.update({ name: datadir for name in listdir(datadir) })
  torrents = []
  for torrentdir in cmdline.torrentdir:
    torrents.extend(glob(path.join(torrentdir, '*.torrent')))

  for torrent in torrents:
    tordata = open(torrent, 'rb').read()
    torrent_name = d8(bdecode(tordata)['info']['name'])
    if torrent_name in data_loc:
      resp = torrent_add(torrent, data_loc[torrent_name], not cmdline.start)
      if resp.success:
        assert('torrent-added' in resp.arguments)
        print e8('Added %s' % path.join(data_loc[torrent_name], torrent_name))
        remove(torrent)
      else:
        print e8('Error ("%s") adding %s' % (resp.error, path.join(data_loc[torrent_name], torrent_name)))
    else:
      print e8('Not found: %s' % torrent_name)
