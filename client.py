from socket import socket
from bittorrent import msg

s = socket()

s.connect(('localhost', 8081))
peer_id = 'b'*20
print 'peer_id:', peer_id

s.send(msg.Handshake(info_hash='a'*20, peer_id=peer_id))
s.send('\x00\x00\x00\x05\x04\x00\x00\x00\x01')
s.send('hello!')
s.send('hi there')
s.send('\x00\x00\x05\x04\x00\x00\x00\x01')

