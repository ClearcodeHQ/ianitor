# -*- coding: utf-8 -*-
from contextlib import contextmanager
import subprocess
import logging
from requests import ConnectionError

logger = logging.getLogger(__name__)


@contextmanager
def ignore_connection_errors(action="unknown"):
    try:
        yield
    except ConnectionError:
        logger.error("connection error on <%s> action failed" % action)


class Service(object):
    def __init__(self, command, session, ttl, service_name,
                 service_id=None, tags=None, port=None):
        self.command = command
        self.session = session
        self.process = None

        self.ttl = ttl
        self.service_name = service_name
        self.tags = tags or []
        self.port = port
        self.service_id = service_id or service_name

        self.check_id = "service:" + self.service_id

    def start(self):
        """ Start service process.

        :return:
        """
        logger.debug("starting service: %s" % " ".join(self.command))
        self.process = subprocess.Popen(self.command)
        self.register()

    def is_up(self):
        """
        Poll service process to check if service is up.

        :return:
        """
        logger.debug("polling service")
        return bool(self.process) and self.process.poll() is None

    def kill(self):
        """
        Kill service process and make sure it is deregistered from consul
        cluster.

        :return:
        """
        logger.debug("killing service")
        if self.process is None:
            raise RuntimeError("Process does not exist")

        self.process.kill()
        self.deregister()

    def register(self):
        """
        Register service in consul cluster.

        :return: None
        """
        logger.debug("registering service")
        with ignore_connection_errors():
            self.session.agent.service.register(
                name=self.service_name,
                service_id=self.service_id,
                port=self.port,
                tags=self.tags,
                # format it into XXXs format
                ttl="%ss" % self.ttl,
            )

    def deregister(self):
        """
        Deregister service from consul cluster.

        :return: None
        """
        logger.debug("deregistering service")

        with ignore_connection_errors("deregister"):
            self.session.agent.service.deregister(self.service_id)

    def keep_alive(self):
        """
        Keep alive service in consul cluster marking TTL check pass
        on consul agent.

        If some cases it can happen that service registry disappeared from
        consul cluster. This method registers service again if it happens.

        :return: None
        """
        with ignore_connection_errors("ttl_pass"):
            if not self.session.health.check.ttl_pass(self.check_id):
                # register and ttl_pass again if it failed
                logger.warning("service keep-alive failed, re-registering")
                self.register()
                self.session.health.check.ttl_pass(self.check_id)

    def __del__(self):
        """
        Cleanup processes on del
        """
        if self.process and self.process.poll() is None:
            self.kill()
