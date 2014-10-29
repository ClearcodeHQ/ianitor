# -*- coding: utf-8 -*-
# Copyright (C) 2014 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS.md).

# This file is part of ianitor.

# ianitor is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ianitor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with ianitor.  If not, see <http://www.gnu.org/licenses/>.

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
