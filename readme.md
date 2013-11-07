Friendly bittorrent client
--------------------------

Goal is a simple way to test bittorrent client communication.

Requires Twisted and git@github.com:thomasballinger/bittorrent.git (https://github.com/thomasballinger/bittorrent)


TODO
----

* Add error handling to tracker
* Make a torrent file available for download that points to this tracker
* By-connection display of messages (separate sessions for each time connected)
* common tracker request mistake detection, including links to resource on encoding, BT spec, etc.
* implement a simple bittorent client that models per-connection whether it is choked, interested, etc.
* Factor out tacker, peer, and website into different files

ideas
-----

* different torrent files for leeching downloading vs accepting incoming connections
* test suite / goals for having a functioning bittorrent client based on conversations
* strategy test torrents that try things like having one peer that poisons the data
* testing other functionality: distributed hash table, etc.
