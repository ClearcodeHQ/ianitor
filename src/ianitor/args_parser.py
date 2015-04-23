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

import sys
import argparse
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONSUL_HTTP_API_PORT = 8500
DEFAULT_TTL = 10


class CustomFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        # default max_help_position increased for readability
        super(CustomFormatter, self).__init__(prog, max_help_position=50)

    def _format_action_invocation(self, action):
        """
        Hack _format_action_invocation to display metavar for only one
        of options
        """
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar

        parts = []

        # if the Optional doesn't take a value, format is:
        #    -s, --long
        if action.nargs == 0:
            parts.extend(action.option_strings)

        # if the Optional takes a value, format is:
        #    -s ARGS, --long ARGS
        else:
            default = action.dest.upper()
            args_string = self._format_args(action, default)

            # here is the hack: do not add args to first option part
            # if it is both long and short
            if len(action.option_strings) > 1:
                parts.append(action.option_strings[0] + "")
                remaining = action.option_strings[1:]
            else:
                remaining = action.option_strings

            for option_string in remaining:
                parts.append('%s=%s' % (option_string, args_string))

        return ', '.join(parts)

    def add_usage(self, usage, actions, groups, prefix=None):
        """
        Hack add_usage to add fake "-- command [arguments]" to usage
        """
        actions.append(argparse._StoreAction(
            option_strings=[],
            dest="-- command [arguments]"
        ))
        return super(CustomFormatter, self).add_usage(
            usage, actions, groups, prefix
        )


def coordinates(coordinates_string):
    """ parse coordinates string
    :param coordinates_string: string in "hostname" or "hostname:port" format
    :return: (hostname, port) two-tuple
    """
    if ':' in coordinates_string:
        try:
            hostname, port = coordinates_string.split(":")
            port = int(port)

            if not hostname:
                raise ValueError()

        except ValueError:
            raise ValueError("Coordinate should be hostname or hostname:port ")
    else:
        hostname = coordinates_string
        port = DEFAULT_CONSUL_HTTP_API_PORT

    return hostname, port


def get_parser():
    """ Create ianotor argument parser with a set of reasonable defaults
    :return: argument parser
    """
    parser = argparse.ArgumentParser(
        "ianitor",
        description="Doorkeeper for consul discovered services.",
        formatter_class=CustomFormatter,
    )

    parser.add_argument(
        "--consul-agent",
        metavar="hostname[:port]", type=coordinates, default="localhost",
        help="set consul agent address"
    )

    parser.add_argument(
        "--ttl",
        metavar="seconds", type=float, default=DEFAULT_TTL,
        help="set TTL of service in consul cluster"
    )

    parser.add_argument(
        "--heartbeat",
        metavar="seconds", type=float, default=None,
        help="set process poll heartbeat (defaults to ttl/10)",
    )

    parser.add_argument(
        "--tags",
        action="append", metavar="tag",
        help="set service tags in consul cluster (can be used multiple times)",
    )

    parser.add_argument(
        "--id",
        help="set service id - must be node unique (defaults to service name)"
    )

    parser.add_argument(
        "--port",
        type=int,
        help="set service port",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="count",
        help="enable logging to stdout (use multiple times to increase verbosity)",  # noqa
    )

    parser.add_argument(
        metavar="service-name",
        dest="service_name",
        help="service name in consul cluster",
    )

    return parser


def parse_args():
    """
    Parse program arguments.

    This function ensures that argv arguments after '--' won't be parsed by
    `argparse` and will be returned as separate list.

    :return: (args, command) two-tuple
    """

    parser = get_parser()

    try:
        split_point = sys.argv.index('--')

    except ValueError:
        if "--help" in sys.argv or "-h" in sys.argv or len(sys.argv) == 1:
            parser.print_help()
            exit(0)
        else:
            parser.print_usage()
            print(parser.prog, ": error: command missing")
            exit(1)

    else:
        argv = sys.argv[1:split_point]
        invocation = sys.argv[split_point + 1:]

        args = parser.parse_args(argv)

        # set default heartbeat to ttl / 10. if not specified
        if not args.heartbeat:
            args.heartbeat = args.ttl / 10.
            logger.debug(
                "heartbeat not specified, setting to %s" % args.heartbeat
            )

        return args, invocation
