import curses
from git_process import Commit
from config import *


def commit_render(commit: Commit) -> str:
    return f"{commit._hash} - {commit._date} - {commit._author}"
    
def draw_status_bar(stdscr, dis: int, state: dict) -> None:
    h, w = stdscr.getmaxyx()
    y = h - 2

    status = state["status"]
    status_bar = f" (q to exit) pos: {dis}, h: {h}, w: {w} --{status}--"
  
    stdscr.attron(curses.color_pair(STATUS_PAIR))
    stdscr.addstr(y, 0, status_bar[:w].ljust(w))
    stdscr.attroff(curses.color_pair(STATUS_PAIR))

def base_render(stdscr, commits: list[Commit], pos: int, state: dict) -> None:
    h, w = stdscr.getmaxyx()

    stdscr.attron(curses.color_pair(TEXT_PAIR))
    limit = min(h - 2 - 2, len(commits))
    
    for i in range(0, limit):
        if i == (pos % limit):
            stdscr.addstr(i + 2, 2, commit_render(commits[i]), curses.A_REVERSE)
        else:
            stdscr.addstr(i + 2, 2, commit_render(commits[i]))
            
    stdscr.attroff(curses.color_pair(TEXT_PAIR))

    draw_status_bar(stdscr, pos % limit, state)

def info_render(stdscr, commit: Commit, pos: int, state: dict) -> None:
    h, w = stdscr.getmaxyx()
    msg = commit._msg

    lines = []
    for line in msg.splitlines():
        while len(line) > w - 2:
            lines.append(line[:w - 2])
            line = line[w - 2:]

        if line:
            lines.append(line)
            
    stdscr.attron(curses.color_pair(TEXT_PAIR))

    limit = min(h - 2 - 2, len(lines))

    # TODO: add pager with "j" and "k" keys
    for i in range(0, limit):
        stdscr.addstr(i + 1, 1, lines[i])

    stdscr.attroff(curses.color_pair(TEXT_PAIR))
    draw_status_bar(stdscr, pos % limit, state)
