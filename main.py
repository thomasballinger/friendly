from twisted.web import server, resource
from twisted.web.static import File
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ServerFactory
from bittorrent import bencode

from bittorrent import msg

#TODO config
import os
ip = '54.225.78.167' if os.uname()[1] == 'ip-10-164-74-120' else '127.0.0.1'
hostname = 'torrentb.in' if os.uname()[1] == 'ip-10-164-74-120' else 'localhost'
client_port = 8081
tracker_port = 8100

class Top(resource.Resource):
    def __init__(self, factory):
        self.factory = factory
        resource.Resource.__init__(self)
    def getChild(self, name, request):
        if name == '':
            return self
        else:
            return resource.Resource.getChild(self, name, request)
    def render_GET(self, request):
        suggestions = client_links(p.client_id for p in self.factory.protocols if p.client_id is not None)
        return "<html><h1>Torrentb.in</h1> TODO use a template for this<br/>" + suggestions + "<br/>" + 'Start with <a download="data.torrent" href="/torrent/data.torrent">this torrent file</a>' + "</html>"

def client_links(client_ids):
    links = '\n'.join('<li><a href="/client/'+c+'">'+c+'</a></li>' for c in client_ids)
    suggestions =  """Enter your client id to see its peer conversation <ul>{}</ul>""".format(links)
    return suggestions

class ClientConversations(resource.Resource):
    isLeaf = True
    def __init__(self, factory):
        self.factory = factory
        resource.Resource.__init__(self)
    def render_GET(self, request):
        print request
        print request.uri[8:]
        for p in self.factory.protocols:
            if p.client_id == request.uri[8:]:
                return protocol_info(p.messages, p.data_buffer)
        else:
            return "<html>"+client_links(p.client_id for p in self.factory.protocols if p.client_id is not None)+"</html>"

def protocol_info(message_list, current_buffer):
    li_elements = ''.join(("<li>" + repr(msg) + "</li>") for msg in message_list)
    return template.format(li_elements=li_elements, leftover=repr(current_buffer))

template = """
<html>
<ul>
{li_elements}
</ul>
Not Translated: {leftover}
</html>
"""

class TestTorrents(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        d = bencode.bdecode(open('./torrents/data.torrent').read())
        d['announce'] = 'http://'+hostname+':'+str(tracker_port)+'/announce'
        torrent = bencode.bencode(d)
        return torrent

class BittorrentTracker(resource.Resource): pass
class Announce(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        #TODO implement a tracker!
        d = {}
        d['peers'] = ''.join(chr(int(x)) for x in ip.split('.')) + chr(client_port // 256) + chr(client_port % 256)
        d['interval'] = 10
        d['tracker_id'] = 'asdf'
        d['complete'] = 1
        d['incomplete'] = 1
        return bencode.bencode(d)
class Scrape(resource.Resource):
    #TODO implement scrape!
    def render_GET(self, request):
        d = {}
        d = {'files':{
                      '':{'complete':1,
                          'downloaded':1,
                          'incomplete':0}}}
        return bencode.bencode(d)

class BittorrentProtocol(Protocol):

    def __init__(self, address):
        self.address = address
        self.have_received_handshake = False
        self.client_id = None
        self.messages = []
        self.data_buffer = ''

    def dataReceived(self, data):
        self.data_buffer += data
        print 'received data from', self.address
        print repr(data)
        while True:
            m, self.data_buffer = msg.Msg(bytestring=self.data_buffer)
            if not m:
                break
            print 'processing', m
            self.process_msg(m)
            self.messages.append(m)

    def process_msg(self, m):
        if isinstance(m, msg.Handshake):
            if self.have_received_handshake:
                raise Exception("double handshake!")
            self.have_received_handshake = True
            print 'setting client_id to', m.peer_id
            self.client_id = m.peer_id
        else:
            pass

class BittorrentFactory(ServerFactory):

    def __init__(self, *args, **kwargs):
        self.protocols = []

    def buildProtocol(self, address):
        print 'accepting connection from %r' % address
        p = BittorrentProtocol(address)
        p.factory = self
        self.protocols.append(p)
        return p

def main():
    btf = BittorrentFactory()

    top = Top(btf)
    top.putChild('client', ClientConversations(btf))
    top.putChild('torrent', TestTorrents())
    site = server.Site(top)

    bittorrent_tracker = BittorrentTracker()
    bittorrent_tracker.putChild('announce', Announce())
    bittorrent_tracker.putChild('scrape', Scrape())
    tracker = server.Site(bittorrent_tracker)

    testtorrent = File('./torrent/data.torrent')
    reactor.listenTCP(8080, site)
    reactor.listenTCP(8081, btf)
    reactor.listenTCP(8100, tracker)

if __name__ == "__main__":
    main()
    reactor.run()
