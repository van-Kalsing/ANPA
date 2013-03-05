# -*- coding: utf-8 -*-
import daemon
import glob
import logging
import os
import subprocess
import signal
import sys

_PARENT_PATH = os.path.abspath(os.path.join(os.path.realpath(os.path.dirname(__file__)), os.pardir))
SCRIPTS_PATH = os.path.join(_PARENT_PATH, 'scripts')

RUN_PATH = os.path.realpath(__file__)
RUN_PARAMS_UNIQUE = 'unique'


def scripts():
    #return [name for name in glob.glob(os.path.join(SCRIPTS_PATH, '*.py')) if not 'base.py' in name]
    return glob.glob(os.path.join(SCRIPTS_PATH, '*.py'))


def pids():
    _pids = {}
    ps_command = subprocess.Popen("ps x -o pid= -o cmd= | grep 'python %s'" % SCRIPTS_PATH, shell=True, stdout=subprocess.PIPE)
    ps_out, ps_error = ps_command.communicate()
    ps_command.wait()
    for line in ps_out.split('\n'):
        if line.strip() != '':
            _pid, _cmd = line.strip().split(' ', 1)
            _pids[int(_pid)] = _cmd
    return _pids


def summon(script_name, params=[]):
    with daemon.DaemonContext():
        logging.basicConfig(
            filename=os.path.join(RUN_PATH.replace('.pyc', '.log').replace('.py', '.log')),
            format=u'[%(asctime)s] %(message)s',
            level=logging.INFO
        )
        _pids = pids()
        for pid in _pids:
            if 'python %s' % script_name in _pids[pid] and RUN_PARAMS_UNIQUE in _pids[pid]:
                logging.info('[unique] no run %s' % script_name)
                return
        logging.info('run %s' % script_name)
        proc = subprocess.Popen(['python', script_name] + params)


def unsummon(pid):
    if pid in pids():
        os.kill(pid, signal.SIGTERM)


if __name__ == '__main__':
    summon(sys.argv[1], sys.argv[2:])
