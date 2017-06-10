import time

from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity
from yowsup.layers.protocol_acks.protocolentities import OutgoingAckProtocolEntity
from yowsup.common.tools import Jid

from nltk.chat.rude import rude_chatbot

from .remindme import WhatappBotSetRemider
from .ducked import get_results

import logging
logger = logging.getLogger(__name__)


def construct_reply(recipient, message):
    phone = recipient.split('@')[0]
    rem = WhatappBotSetRemider()

    reply = rem.set_reminder(phone, message) or get_results(message)

    if reply:
        return reply


class SendLayer(YowInterfaceLayer):
    PROP_MESSAGES = "org.openwhatsapp.yowsup.prop.sendclient.queue"

    def __init__(self):
        super(SendLayer, self).__init__()

    def send_message(self, phone, message):

        entity = TextMessageProtocolEntity(message, to=phone)
        self.toLower(entity)

    @ProtocolEntityCallback("success")
    def onSuccess(self, successProtocolEntity):

        for target in self.getProp(self.__class__.PROP_MESSAGES, []):
            phone, message = target
            print(phone, message, "From on success")
            messageEntity = TextMessageProtocolEntity(message, to=Jid.normalize(phone))
            self.toLower(messageEntity)

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", "delivery", entity.getFrom())
        self.toLower(ack)

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):

        if messageProtocolEntity.getType() == 'text':

            namemitt = messageProtocolEntity.getNotify()
            recipient = messageProtocolEntity.getFrom()
            message = messageProtocolEntity.getBody().lower()

            reply = construct_reply(recipient, message)

            if not reply:
                if message.startswith("hello"):
                    reply = "Hi " + namemitt

                else:
                    reply = rude_chatbot.respond(message)

            resp = TextMessageProtocolEntity(reply, to=recipient)
            self.toLower(resp)

            self.toLower(messageProtocolEntity.ack())
            time.sleep(0.5)
            self.toLower(messageProtocolEntity.ack(True))

        else:
            print("foo")
