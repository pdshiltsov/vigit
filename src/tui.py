from git_process import Commit, get_commits
from popups import draw_commit_info_popup
import curses

# Color configuration
TEXT_FG = curses.COLOR_WHITE
TEXT_BG = curses.COLOR_BLACK

STATUS_FG = curses.COLOR_BLACK
STATUS_BG = curses.COLOR_CYAN

TEXT_PAIR = 1
STATUS_PAIR = 2


def init_colors() -> None:
    if not curses.has_colors():
        return

    curses.start_color()

    # Initialize color pairs
    curses.init_pair(TEXT_PAIR, TEXT_FG, TEXT_BG)
    curses.init_pair(STATUS_PAIR, STATUS_FG, STATUS_BG)


def commit_render(commit: Commit) -> str:
    return f"{commit._hash} - {commit._date} - {commit._author}"
    
def draw_status_bar(stdscr, text: str) -> None:
    h, w = stdscr.getmaxyx()
    y = h - 2

    stdscr.attron(curses.color_pair(STATUS_PAIR))
    stdscr.addstr(y, 0, text[:w].ljust(w))
    stdscr.attroff(curses.color_pair(STATUS_PAIR))

def render(stdscr, commits: list[Commit], pos: int, state: bool) -> None:
    h, w = stdscr.getmaxyx()

    stdscr.attron(curses.color_pair(TEXT_PAIR))
    # stdscr.addstr(0, 2, commits.__repr__())
    limit = min(h - 2 - 2, len(commits))
    
    for i in range(0, limit):
        if i == (pos % limit):
            stdscr.addstr(i + 2, 2, commit_render(commits[i]), curses.A_REVERSE)
        else:
            stdscr.addstr(i + 2, 2, commit_render(commits[i]))
            
    stdscr.attroff(curses.color_pair(TEXT_PAIR))

    # status bar
    if state:
        status_bar = f" (q to exit) pos: {(pos % limit)}, h: {h}, w: {w} --PopUp--"
    else:
        status_bar = f" (q to exit) pos: {(pos % limit)}, h: {h}, w: {w} --Normal--"

    draw_status_bar(stdscr, status)


def main(stdscr) -> None:
    curses.curs_set(0)
    stdscr.keypad(True)

    init_colors()
    commits = get_commits()

    state = {
        "popup": False,
        "win": None,
        "status": "base"
    }

    y = 0
    while True:
        stdscr.erase()
        stdscr.refresh()
    
        render(stdscr, commits, y, state["popup"])
    
        if state["popup"] and state["win"] is not None:
            state["win"].refresh()

        if state["popup"]:
            if state["win"] is None:
                state["win"] = draw_commit_info_popup(stdscr, commits[y])

        key = stdscr.getch()

        if key == ord("q"):
            if state["popup"]:
                state["win"] = None
                state["popup"] = False
            else:
                state["exit"] = True
            
        elif key == ord("j"):
            y += 1

        elif key == ord("k"):
            if y - 1 >= 0:
                y -= 1

        elif key == ord("s"):
            state["win"] = draw_commit_info_popup(stdscr, commits[y])
            state["popup"] = True
            
        elif key in (curses.KEY_ENTER, 10, 13):
            state["win"] = draw_commit_info_popup(stdscr, commits[y])
            state["popup"] = True

        else:
            pass # Passing

        
if __name__ == "__main__":
    curses.wrapper(main)
