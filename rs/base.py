# -*- coding: utf-8 -*-
import os
import inspect
import logging
import time

import zmq
from zmq.eventloop import ioloop


PUB_PORT = 6001
SUB_PORT = 6002

SUBKEY_EXIT = '[exit]'


class RSPubIsNoneException(Exception):
    pass


class RSBase(object):
    subscribe = [SUBKEY_EXIT]
    is_publisher = True

    def __init__(self):
        self.pid = os.getpid()

        self._init_logging()
        self.log('init script, pid:%s' % self.pid)

        self.context = zmq.Context()
        if self.subscribe:
            self._init_subscribe()
        else:
            self.sub_sock = None
        if self.is_publisher:
            self._init_publisher()
        else:
            self.pub_sock = None

        self.run()

        if self.sub_sock:
            self.sub_sock.close()
        if self.pub_sock:
            self.pub_sock.close()
        self.context.term()
        self.log('end')

    def _init_logging(self):
        logging.basicConfig(
            filename=inspect.getfile(self.__class__).replace('.pyc', '.log').replace('.py', '.log'),
            format=u'[%(asctime)s] %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger()

    def log(self, text):
        self.logger.info(text)

    def _init_subscribe(self):
        self.sub_sock = self.context.socket(zmq.SUB)
        self.sub_sock.connect('tcp://localhost:%s' % SUB_PORT)
        for sub in self.subscribe:
            self.sub_sock.setsockopt(zmq.SUBSCRIBE, sub)
        self.log('init subscribe')

    def _on_recv(self, sock, events):
        key, message = self.sub_sock.recv_multipart()
        self.recv(key, message)
        if key == SUBKEY_EXIT and message in ['all', str(self.pid)]:
            self.loop.stop()

    def recv(self, key, message):
        #pass
        print key, message 

    def _init_publisher(self):
        self.pub_sock = self.context.socket(zmq.PUB)
        self.pub_sock.connect('tcp://localhost:%s' % PUB_PORT)
        self.log('init publisher')

    def send(self, key, message):
        if self.pub_sock:
            self.pub_sock.send_multipart([str(key), str(message)])
        else:
            raise RSPubIsNoneException()

    def run(self):
        if self.sub_sock:
            self.loop = ioloop.IOLoop.instance()
            self.loop.add_handler(self.sub_sock, self._on_recv, zmq.POLLIN)
            self.loop.start()
