import os
from yowsup.stacks import YowStackBuilder
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent
from yowsup.layers.auth import YowAuthenticationProtocolLayer
from yowsup.layers.network import YowNetworkLayer

from yowsup.common import YowConstants
from yowsup.env import YowsupEnv
from yowsup.layers.coder import YowCoderLayer

from layers.sendlayer import SendLayer


CREDENTIALS = ("919972385823", "T58HwIG6QrLgreNFBzhOxOcCdSQ=")


def setup():
    module = os.path.split(os.path.dirname(__file__))[-1]
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{}.settings".format(module))


if __name__ == "__main__":

    setup()

    stackBuilder = YowStackBuilder()

    stack = stackBuilder.pushDefaultLayers(True).push(SendLayer).build()

    stack.setProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS, CREDENTIALS)
    stack.setProp(YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0])
    stack.setProp(YowCoderLayer.PROP_DOMAIN, YowConstants.DOMAIN)
    stack.setProp(YowCoderLayer.PROP_RESOURCE, YowsupEnv.getCurrent().getResource())
    stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
    try:
            stack.loop(timeout=0.5, discrete=0.5)
            print("Done")
    except AuthError as e:
            print("Authentication Error: %s" % e.message)
