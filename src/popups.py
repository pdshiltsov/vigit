from git_process import Commit
import curses


def draw_commit_info_popup(stdscr, commit: Commit):
    h, w = stdscr.getmaxyx()

    height = 10
    width = 40

    y = (h - height) // 2
    x = (w - width) // 2

    win = curses.newwin(height, width, y, x)
    win.box()

    win.addstr(1, 1, commit._msg)
    # win.addstr(5, 2, "(q to exit)")

    return win
