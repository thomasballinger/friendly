from socket import socket
from bittorrent import msg
from main import main
from main import BittorrentFactory
from twisted.internet.defer import Deferred


def peer_connect():
    s = socket()

    s.connect(('localhost', 8081))
    peer_id = 'b'*20

    s.send(msg.Handshake(info_hash='a'*20, peer_id=peer_id))
    s.send('\x00\x00\x00\x05\x04\x00\x00\x00\x01')
    s.send('hello!')
    s.send('hi there')
    s.send('\x00\x00\x05\x04\x00\x00\x00\x01')

    from twisted.internet import reactor
    reactor.callLater(3, d.callback, None)

def test_peer_connect(res):
    assert len(btf.protocols) == 1
    return "finished"

def end(res):
    print res
    reactor.stop()

#main()
d = Deferred()
d.addCallback(test_peer_connect)
d.addBoth(end)

from twisted.internet import reactor
btf = BittorrentFactory()
reactor.callLater(0,peer_connect)
reactor.listenTCP(8081, btf)
reactor.run()
