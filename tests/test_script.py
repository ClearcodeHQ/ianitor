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
from mock import patch


from ianitor.service import Service
import ianitor.script


@patch('sys.argv', ["ianitor", "tail", "--", "tail", '-f', '/dev/null'])
def test_script_main(consul_instance):
    """Run ianitor.script.main and mock service is_up so it will quit
    immediately"""

    with patch.object(Service, "is_up", return_value=False) as is_up:
        ianitor.script.main()
        is_up.assert_any_call()
