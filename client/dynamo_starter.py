#!/usr/bin/env python
import argparse
import os
import traceback
from multiprocessing import Event
from multiprocessing import Process

import time

import sys

from generic_mounter import Mounter
from dynamo import Dynamo
from logger import pubsub_logger
from config import DYNAMO_PATH, MAX_WORKERS_PER_CLIENT, CLIENT_MOUNT_POINT
from utils import shell_utils


def run_worker(event, mounter, controller, server, nodes, domains, proc_id):
    worker = Dynamo(event, mounter, controller, server, nodes, domains, proc_id)
    worker.run()


def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(
        description='Test Runner script')
    parser.add_argument('-c', '--controller', type=str, required=True, help='Controller host name')
    parser.add_argument('-s', '--server', type=str, required=True, help='Cluster Server hostname')
    parser.add_argument('-e', '--export', type=str, help='NFS Export Name', default="vol0")
    parser.add_argument('-n', '--nodes', type=int, help='Number of active nodes', required=True)
    parser.add_argument('-d', '--domains', type=int, help='Number of fs domains', required=True)
    parser.add_argument('-m', '--mtype', type=int, help='Mount Type', default=3)
    args = parser.parse_args()
    return args


def run():
    stop_event = Event()
    processes = []
    args = get_args()
    logger = pubsub_logger.PUBLogger(args.controller).logger
    time.sleep(10)
    try:
        os.chdir('/qa/dynamo/client')
        logger.info("Mounting work path...")
        mounter = Mounter(args.server, args.export, args.mtype, 'DIRSPLIT', logger, args.nodes, args.domains)
        mounter.mount()
    except Exception as error_on_init:
        logger.error(str(error_on_init) + " WorkDir: {0}".format(os.getcwd()))
        raise
    # Start a few worker processes
    for i in range(MAX_WORKERS_PER_CLIENT):
        processes.append(Process(target=run_worker,
                                 args=(stop_event, mounter, args.controller, args.server, args.nodes,
                                       args.domains, i,)))
    for p in processes:
        p.start()
    try:
        time.sleep(5)
        # The controller will set the stop event when it's finished, just
        # idle until then
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()
    else:
        logger.exception()
        raise
    logger.info('waiting for processes to die...')
    for p in processes:
        p.join()
    logger.info('all done')


if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
