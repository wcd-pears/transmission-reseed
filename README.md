about
-----

This is a script for re-seeding multiple torrents into Transmission.

The assumed use case is that you have a bunch of .torrent files, and
all the associated data (perhaps in more than one location), and you
need to import these into Transmission, with each one pointed to the
correct location.  Transmission makes this kind of a pain in the ass if
you import by hand.

prerequisites
-------------

You will need the RPC interface (a.k.a. web client) enabled, the
Python *requests* module, and the Python *bencode* module.

These can be installed with pip or easy\_install from a terminal:

    sudo pip install requests
    sudo pip install bencode

OR

    sudo easy_install requests
    sudo easy_install bencode

usage
-----

    ./reseed.py --torrentdir /home/me/Downloads --datadir /media/music --datadir /home/me/Music

This example will look for torrent files in /home/me/Downloads, and
will attempt to match up these files to data in /media/music or
/home/me/Music.  If a match is found, the torrent will be imported,
with the download directory pointing to the location where the match
was found.  The .torrent file will be removed (Transmission will keep
its own copy).  In the case no match is found, the .torrent file will
be ignored and left where it is.

The script only looks at the top-level torrent name, and doesn't look
inside at nested filenames or content, so it may be fooled in some
cases.  Exercise caution, and pay attention to Transmission's hash
check results.
