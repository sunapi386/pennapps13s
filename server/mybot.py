from chatterbotapi import ChatterBotFactory, ChatterBotType


class ChatterBot(object):

    def __init__(self, bot):
        if bot.lower() == 'cleverbot':
            self.bot = ChatterBotFactory().create(ChatterBotType.CLEVERBOT).create_session()
        elif bot.lower() == 'jabberwacky':
            self.bot = ChatterBotFactory().create(ChatterBotType.JABBERWACKY).create_session()
        else:
            self.bot = ChatterBotFactory().create(ChatterBotType.PANDORABOTS, 'f6d4afd83e34564d').create_session()

    def respond_to(self, msg):
        return self.bot.think(msg)

