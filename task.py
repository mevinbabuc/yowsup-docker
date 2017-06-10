import os
import time

from threading import Thread
from yowsup.stacks import YowStackBuilder
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent
from yowsup.layers.auth import YowAuthenticationProtocolLayer
from yowsup.layers.network import YowNetworkLayer

from yowsup.common import YowConstants
from yowsup.env import YowsupEnv
from yowsup.layers.coder import YowCoderLayer

from layers.sendlayer import SendLayer
from layers.remindme import WhatappBotSetRemider


CREDENTIALS = ("919972385823", "T58HwIG6QrLgreNFBzhOxOcCdSQ=")


def setup():
    module = os.path.split(os.path.dirname(__file__))[-1]
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{}.settings".format(module))


def check_for_reminder_messages(stack):
    print("Thread started", ...)
    bot = WhatappBotSetRemider()

    while True:
        time.sleep(30)
        raw_messages = bot.get_messages()
        print('Check messages', raw_messages)

        for msg in raw_messages:
            stack.send_message(msg['phone'] + '@s.whatsapp.net', msg['message'])
            bot.expire_reminder(msg)


if __name__ == "__main__":

    setup()

    stackBuilder = YowStackBuilder()

    send_layer = SendLayer()

    stack = stackBuilder.pushDefaultLayers(True).push(send_layer).build()

    stack.setProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS, CREDENTIALS)
    stack.setProp(YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0])
    stack.setProp(YowCoderLayer.PROP_DOMAIN, YowConstants.DOMAIN)
    stack.setProp(YowCoderLayer.PROP_RESOURCE, YowsupEnv.getCurrent().getResource())
    stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))

    try:

        print("Starting thread")

        t = Thread(target=check_for_reminder_messages, args=(send_layer, ))
        t.start()

        print("Starting the loop")
        stack.loop(timeout=0.5, discrete=0.5)
        print("Done")
    except AuthError as e:
        print("Authentication Error: %s" % e.message)
