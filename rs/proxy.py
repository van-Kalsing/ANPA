# -*- coding: utf-8 -*-
import zmq

from rs import base

def run():
    try:
        context = zmq.Context()
        frontend = context.socket(zmq.SUB)
        frontend.bind("tcp://*:%s" % base.PUB_PORT) 
        frontend.setsockopt(zmq.SUBSCRIBE, "")
        backend = context.socket(zmq.PUB)
        backend.bind("tcp://*:%s" % base.SUB_PORT)
        zmq.device(zmq.FORWARDER, frontend, backend)
    except Exception, e:
        print e
        print 'bringing down zmq device'
    finally:
        frontend.close()
        backend.close()
        context.term()
