#!/usr/bin/python

import xmpp
from chatterbotapi import ChatterBotFactory, ChatterBotType
from credentials import FACEBOOK_ID, PASS, SERVER

jid = xmpp.protocol.JID(FACEBOOK_ID)
C = xmpp.Client(jid.getDomain(), debug=[])

# capture errors
if not C.connect((SERVER, 5222)):
    raise IOError('Cannot connect to server!')

#C.connect((SERVER, 5222))
#C.auth(jid.getNode(), PASS)
if not C.auth(jid.getNode(), PASS):
    raise IOError('Cannot authenticate with server.')

# all available IDs to send message to
#C.sendInitPresence(requestRoster=1)
#for ro in C.getRoster().getItems():
#    print ro

cleverbot = ChatterBotFactory().create(ChatterBotType.CLEVERBOT).create_session()
#jabberwacky = ChatterBotFactory().create(ChatterBotType.JABBERWACKY).create_session()
#pandorabots = ChatterBotFactory().create(ChatterBotType.PANDORABOTS, 'f6d4afd83e34564d').create_session()

C.send(xmpp.protocol.Message('-535102603@chat.facebook.com', cleverbot.think('Hello!')))
#C.send(xmpp.protocol.Message('-535102603@chat.facebook.com', jabberwacky.think('Hello!')))
#C.send(xmpp.protocol.Message('-535102603@chat.facebook.com', pandorabots.think('Hello!')))

cl.disconnect()

