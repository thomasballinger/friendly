from twisted.web import server, resource
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory, ServerFactory

from bittorrent import msg

class Simple(resource.Resource):
    isLeaf = True
    def __init__(self, factory):
        self.factory = factory
    def render_GET(self, request):
        print repr(request.uri)
        client_id = request.uri[1:]
        if len(client_id) != 20:
            return """<html>Enter your client id to see its peer conversation <ul>{}</ul></html>""".format('\n'.join('<li><a href="/'+p.client_id+'">'+p.client_id+'</a></li>' for p in self.factory.protocols))
        for p in self.factory.protocols:
            print p
            if p.client_id == request.uri[1:]:
                return protocol_info(p.messages, p.data_buffer)
        else:
            return "<html> I don't see that client</html>"

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

class BittorrentProtocol(Protocol):

    def __init__(self, address):
        self.address = address
        self.have_receieved_handshake = False
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
            if self.have_receieved_handshake:
                raise Exception("double handshake!")
            self.have_receieved_handshake = True
            print 'setting client_id to', m.peer_id
            self.client_id = m.peer_id
        else:
            pass

class BittorrentFactory(ServerFactory):
    protocol = BittorrentProtocol

    def __init__(self, *args, **kwargs):
        self.protocols = []

    def buildProtocol(self, address):
        print 'accepting connection from %r' % address
        p = self.protocol(address)
        p.factory = self
        self.protocols.append(p)
        return p

btf = BittorrentFactory()
site = server.Site(Simple(btf))
reactor.listenTCP(8080, site)
reactor.listenTCP(8081, btf)
reactor.run()
