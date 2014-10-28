# -*- coding: utf-8 -*-
import pytest
from mock import patch

from ianitor import args_parser


def test_coordinates():
    assert args_parser.coordinates("localhost:1222") == ("localhost", 1222)

    assert args_parser.coordinates("localhost") == (
        "localhost", args_parser.DEFAULT_CONSUL_HTTP_API_PORT
    )

    with pytest.raises(ValueError):
        args_parser.coordinates("localhost:12:")

    with pytest.raises(ValueError):
        args_parser.coordinates("localhost:")

    with pytest.raises(ValueError):
        args_parser.coordinates(":123")


@patch('sys.argv', ["ianitor", "tailf", '--', 'tailf', 'something'])
def test_parse_args():
    args, invocation = args_parser.parse_args()
    assert invocation == ['tailf', 'something']

TEST_TTL = 100


@patch('sys.argv', ["ianitor", "tailf", '--ttl', str(TEST_TTL), '--', 'tailf', 'something'])  # noqa
def test_default_heartbeat():
    args, invocation = args_parser.parse_args()
    assert args.heartbeat == TEST_TTL / 10.
