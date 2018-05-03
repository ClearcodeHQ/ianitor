import shlex
import subprocess
import time
import os

import pytest

CONSUL_BIN = os.environ.get(
    "CONSUL_BIN",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'consul')
)
CONSUL_DATA_DIR = os.environ.get('CONSUL_DATA_DIR', '/tmp/consul')


@pytest.fixture(scope="session")
def consul_instance():

    command = '{bin} agent -server -data-dir {datadir} -bootstrap-expect=1' \
              ''.format(bin=CONSUL_BIN, datadir=CONSUL_DATA_DIR)

    command = command.format(bin=bin).strip()
    command = shlex.split(command)

    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    time.sleep(10)

    yield proc

    proc.terminate()
