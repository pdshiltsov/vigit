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

from src.git_process import Commit, get_commits
from src.render import base_render, info_render
from src.config import *
from src.fsm import LSI
import curses


def init_colors() -> None:
    if not curses.has_colors():
        return

    curses.start_color()

    # Initialize color pairs
    curses.init_pair(TEXT_PAIR, TEXT_FG, TEXT_BG)
    curses.init_pair(STATUS_PAIR, STATUS_FG, STATUS_BG)

def main(stdscr) -> None:
    curses.curs_set(0)
    stdscr.keypad(True)

    init_colors()
    commits = get_commits()

    state = LSI(["base", "info"])

    y = 0
    pager_pos = 0
    pos_limit = -1
    saved_info = None
    while True:
        stdscr.erase()
        stdscr.refresh()

        match state.status:
            case "base":
                pos_limit = base_render(stdscr, commits, y, state)
            case "info":
                pos_limit = info_render(stdscr, saved_info, pager_pos, state)
                
        key = stdscr.getch()

        match state.status: 
            case "base":
                if key == ord("q"):
                    break

                elif key == ord("j"):
                    if y < pos_limit:
                        y += 1

                elif key == ord("k"):
                    if y - 1 >= 0:
                        y -= 1

                elif key in (curses.KEY_ENTER, 10, 13):
                    state.following()
                    saved_info = commits[y % len(commits)]
                else:
                    pass

            case "info":
                if key == ord("q"):
                    state.previous()
                    saved_info = None
                    pager_pos = 0

                elif key == ord("j"):
                    if pager_pos < pos_limit:
                        pager_pos += 1

                elif key == ord("k"):
                    if pager_pos - 1 >= 0:
                        pager_pos -= 1

                elif key == ord("p"):
                    # TODO, add parents
                    pass
                    
                else:
                    pass

            case _:
                pass # Undefined status
        
        
if __name__ == "__main__":
    curses.wrapper(main)
