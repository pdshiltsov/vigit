# vigit - Minimal TUI application for working with Git directly from the terminal.
# Copyright (C) 2026 vigit Pavel Shiltsov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import curses


TEXT_FG = curses.COLOR_WHITE
TEXT_BG = curses.COLOR_BLACK

STATUS_FG = curses.COLOR_BLACK
STATUS_BG = curses.COLOR_CYAN

TEXT_PAIR = 1
STATUS_PAIR = 2
SELECTED_PAIR = 3


# you can change this section
commit_selected = "● "
commit_not_selected = "○ "

SELECTED = curses.COLOR_CYAN
