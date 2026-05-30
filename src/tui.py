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
from src.fsm import LSI, FSM
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

    states = {
        "normal": LSI(["base", "info"]),
        "parents": LSI(["base", "info"])
    }

    fsm = FSM(states)
    
    y = 0 # eliminate
    saved_pos = 0 # eliminate
    pager_pos = 0 # eliminate
    pos_limit = -1
    saved_info = None # eliminate
    current_info = None # eliminate
    parents_current_info = None # eliminate
    while True:
        stdscr.erase()
        stdscr.refresh()
        if fsm.pos == "normal":
            fsm.state.info["info"] = commits
        else:
            fsm.state.info["info"] = parents_current_info
            
        match fsm.state.status:
            case "base":
                pos_limit = base_render(stdscr, fsm.state.info["info"], fsm.state.info["cursor"], fsm.state)
            case "info":
                pos_limit = info_render(stdscr, fsm.state.info["info"], fsm.state.info["cursor"], fsm.state)
                
        key = stdscr.getch()

        match fsm.state.status: 
            case "base":
                if key == ord("q"):
                    if fsm.pos == "normal":
                        break
                    else:
                        fsm.change_state("normal")

                elif key == ord("j"):
                    if fsm.state.info["cursor"] + 1 < pos_limit:
                        fsm.state.info["cursor"] += 1

                elif key == ord("k"):
                    if fsm.state.info["cursor"] - 1 >= 0:
                        fsm.state.info["cursor"] -= 1

                elif key in (curses.KEY_ENTER, 10, 13):
                    tmp = fsm.state.info
                    fsm.state.following()
                    fsm.state.info["info"] = tmp["info"][tmp["cursor"]]
                else:
                    pass

            case "info":
                if key == ord("q"):
                    fsm.state.previous()
                    fsm.state.info["info"] = None
                    fsm.state.info["cursor"] = 0

                elif key == ord("j"):
                    if fsm.state.info["cursor"] < pos_limit:
                        fsm.state.info["cursor"] += 1

                elif key == ord("k"):
                    if fsm.state.info["cursor"] - 1 >= 0:
                        fsm.state.info["cursor"] -= 1

                elif key == ord("p") and fsm.pos == "normal": # to avoid multiple parents opening
                    tmp = fsm.state.info["info"].parents

                    fsm.change_state("parents")
                    fsm.state.previous() # 100% base
                    
                else:
                    pass

            case _:
                pass # Undefined status
        
        
if __name__ == "__main__":
    curses.wrapper(main)
