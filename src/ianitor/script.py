# -*- coding: utf-8 -*-
from time import sleep
import signal
import logging

import consul

from ianitor.service import Service
from ianitor.args_parser import parse_args


SIGNALS = [
    member
    for member
    in dir(signal)
    if member.startswith("SIG") and '_' not in member
]


logger = logging.getLogger(__name__)


def setup_logging(verbosity):
    ilogger = logging.getLogger('ianitor')

    if verbosity:
        handler = logging.StreamHandler()
        if verbosity == 1:
            handler.setLevel(logging.ERROR)
        if verbosity == 2:
            handler.setLevel(logging.WARNING)
        if verbosity >= 3:
            handler.setLevel(logging.DEBUG)
    else:
        handler = logging.NullHandler()

    formatter = logging.Formatter(
        '[%(levelname)s] %(name)s: %(message)s'
    )

    handler.setFormatter(formatter)
    ilogger.setLevel(logging.DEBUG)
    ilogger.addHandler(handler)


def main():
    args, command = parse_args()
    setup_logging(args.verbose)

    session = consul.Consul(*args.consul_agent)

    service = Service(
        command,
        session=session,
        ttl=args.ttl,
        service_name=args.service_name,
        service_id=args.id,
        tags=args.tags,
        port=args.port
    )

    service.start()

    def signal_handler(signal_number, *_):
        service.process.send_signal(signal_number)

    for signal_name in SIGNALS:
        try:
            signum = getattr(signal, signal_name)
            signal.signal(signum, signal_handler)
        except RuntimeError:
            # signals that cannot be catched will raise RuntimeException
            pass

    while sleep(args.heartbeat) or service.is_up():
        service.keep_alive()

    logger.info("process quit with errorcode %s %s" % (
        service.process.poll(),
        "(signal)" if service.process.poll() < 0 else ""
    ))

    service.deregister()
