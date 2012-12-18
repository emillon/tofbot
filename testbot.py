from bot import Tofbot
import unittest
from collections import namedtuple


def print_resp(msg):
    print (" -> %s" % msg)


class TestTofbot(Tofbot):

    def __init__(self, nick, name, chan, origin):
        chans = [chan]
        self.nick = nick
        Tofbot.__init__(self, nick, name, chans, debug=False)
        self.chan = chan
        self.origin = origin
        self.cb = None

    def msg(self, chan, msg):
        if self.cb:
            self.cb(msg)
        else:
            print_resp(msg)

    def send(self, msg):
        print ("<-  %s" % msg)
        self.dispatch(self.origin, [msg, 'PRIVMSG', self.chan])

    def kick(self, msg=None):
        if msg is None:
            msg = self.nick
        self.dispatch(self.origin, [msg, 'KICK', self.chan, self.nick])


class BotAction:
    def __init__(self, bot, action):
        self.bot = bot
        self.action = action

    def __enter__(self):
        msgs = []

        def capture_out(msg):
            msgs.append(msg)

        self.bot.cb = capture_out
        self.action()
        return msgs[0]

    def __exit__(self, *args):
        pass


def bot_input(bot, msg):
    return BotAction(bot, lambda: bot.send(msg))


def bot_kick(bot, msg=None):
    return BotAction(bot, lambda: bot.kick(msg))


class TestCase(unittest.TestCase):

    def setUp(self):
        nick = "testbot"
        name = "Test Bot"
        chan = "#chan"
        Origin = namedtuple('Origin', ['sender', 'nick'])
        origin = Origin('sender', 'nick')
        self.bot = TestTofbot(nick, name, chan, origin)
        cmds = ['!set autoTofadeThreshold 100']
        for cmd in cmds:
            self.bot.dispatch(origin, [cmd, 'BOTCONFIG', 'PRIVMSG', '#config'])

        self.bot.joined = True

    def test_set_allowed(self):
        msg = "!set autoTofadeThreshold 9000"
        self.bot.send(msg)

        with bot_input(self.bot, "!get autoTofadeThreshold") as l:
            self.assertEqual(l, "autoTofadeThreshold = 9000")

    def test_kick(self):
        with bot_kick(self.bot) as l:
            self.assertEqual(l, "respawn, LOL")
