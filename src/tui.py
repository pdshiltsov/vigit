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
from src.git_process import get_changed_files, get_file_diff
from src.git_process import get_files
from src.analyzer import analyze_repo, RISK_RULES
from src.render import base_render, info_render, license_render
from src.render import render_file_analyze
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
    curses.init_pair(SELECTED_PAIR, SELECTED, TEXT_BG)

def license(stdscr, text: str) -> None:
    curses.curs_set(0)
    stdscr.keypad(True)

    init_colors()

    cursor = 0
    while True:
        stdscr.erase()
        stdscr.refresh()
        limit = license_render(stdscr, text, cursor)
        key = stdscr.getch()
        
        if key == ord("q"): break
        elif key == ord("j"):
            if cursor + 1 < limit:
                cursor += 1
                    
        elif key == ord("k"):
            if cursor > 0:
                cursor -= 1
                    

def no_git(stdscr, err: str) -> None:
    curses.curs_set(0)
    stdscr.keypad(True)

    init_colors()
    
    text = f"""
0       0 0000000 0000000 0000000 0000000
 0     0     0    0          0       0
  0   0      0    0   000    0       0
   0 0       0    0     0    0       0
    0     0000000 0000000 0000000    0

      > {err}
        (press any key to exit)

vigit Copyright (C) 2026
see `vigit --license` for more details.
    
    """
    
    while True:
        stdscr.erase()
        stdscr.refresh()
        stdscr.addstr(0, 0, text)
        if stdscr.getch():
            break
        
def main(stdscr) -> None:
    curses.curs_set(0)
    stdscr.keypad(True)

    init_colors()
    commits = get_commits()

    states = {
        "normal": LSI(["base", "info"]),
        "parents": LSI(["base", "info"]),
        "diff": LSI(["base", "info"]),
        "analyzer": LSI(["info"])
    }

    fsm = FSM(states)
    fsm.state.info["info"] = commits 
    
    pos_limit = -1
    while True:
        stdscr.erase()
        stdscr.refresh()
            
        match fsm.state.status:
            case "base":
                pos_limit = base_render(stdscr, fsm.state.info["info"], fsm.state.info["cursor"], fsm.state)
            case "info":
                pos_limit = info_render(stdscr, fsm.state.info["info"], fsm.state.info["cursor"], fsm.state)
                
        key = stdscr.getch()
        
        if fsm.pos == "analyzer" and key == ord("q"):
            fsm.change_state("normal")
            continue

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
                    tmp_info, tmp_cursor = fsm.state.info["info"], fsm.state.info["cursor"]
                    if not (len(tmp_info) == 0 and fsm.pos == "parents"):
                        fsm.state.following()
                        fsm.state.info["info"] = tmp_info[tmp_cursor]
                        
                    if fsm.pos == "diff":
                        curr_diff = get_file_diff(fsm.state.commit, tmp_info[tmp_cursor][1]) 
                        fsm.state.following()
                        fsm.state.info["info"] = curr_diff
                        
                elif key == ord("a"):
                    fsm.change_state("analyzer")
                    fsm.state.info["info"] = render_file_analyze(analyze_repo(get_files(), RISK_RULES))
                    
                else:
                    pass

            case "info":
                if key == ord("q"):
                    fsm.state.info["info"] = None
                    fsm.state.info["cursor"] = 0
                    fsm.state.previous()

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
                    fsm.state.info["info"] = tmp

                elif key == ord("d") and fsm.pos != "diff":
                    commit = fsm.state.info["info"]
                    tmp = get_changed_files(commit)

                    fsm.change_state("diff")
                    fsm.state.previous() # 100% base
                    fsm.state.info["info"] = tmp
                    fsm.state.commit = commit

                else:
                    pass

            case _:
                pass # Undefined status
        
        
if __name__ == "__main__":
    curses.wrapper(main)
