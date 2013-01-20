import logging
from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout

from mybot import ChatterBot

# Ke Sun
#RECIPIENT = '-535102603@chat.facebook.com'
USERNAME = 'rawkcy'
PASSWORD = 'tofumaster'

class EchoBot(ClientXMPP):

    def __init__(self, jid, password, bot):
        ClientXMPP.__init__(self, jid, password)

        self.bot = bot
        #self.recipient = RECIPIENT
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()
        #self.send_message(mto=self.recipient,
        #                  mbody='Hello!',
        #                  mtype='chat')

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            msg.reply("%s" % self.bot.respond_to(msg['body'])).send()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    xmpp = EchoBot('%s@chat.facebook.com' % USERNAME, PASSWORD, ChatterBot('cleverbot'))
    if xmpp.connect():
        xmpp.process(block=True)
        print "Done."
    else:
        print "Unable to connect."

