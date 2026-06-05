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
from src.git_process import Commit
from src.config import *
from datetime import datetime 


def get_text(commit: Commit) -> str:
    def format_person(name: str, email: str, ts: int) -> str:
        date = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        return f"Name: {name} <{email}>\n\tDate: {date}"

    parents = "\n".join(f"\t{p.hash}" for p in commit.parents) if commit.parents else "\tnone"
    refs = ", ".join(commit.refs) if commit.refs else "none"

    return f"""\
NAME
\t{commit.short_hash} - {commit.subject}

SYNOPSIS
\tgit show {commit.hash.strip()}

DESCRIPTION
\t{commit.body or "No description provided."}

AUTHOR
\t{format_person(commit.author_name, commit.author_email, commit.author_ts)}

COMMITTER
\t{format_person(commit.committer_name, commit.committer_email, commit.committer_ts)}

REFERENCES
\t{refs}

PARENTS (press p to see more, you can't see parents of parents)
{parents}
"""

def commit_render(commit: Commit) -> str:
    ts = datetime.fromtimestamp(commit.committer_ts)
    readable_time = ts.strftime("%Y-%m-%d %H:%M")

    return f"{commit.short_hash} | {readable_time} | {commit.committer_name}"    
def draw_status_bar(stdscr, dis: int, state: dict) -> None:
    h, w = stdscr.getmaxyx()

    status = state.status
    status_bar = f" (q: exit, j/k: navigate, enter: details, p: see parents) pos: {dis} --{status}--"
  
    stdscr.attron(curses.color_pair(STATUS_PAIR))
    stdscr.addstr(h - 2, 0, status_bar[:w].ljust(w))
    stdscr.attroff(curses.color_pair(STATUS_PAIR))

def base_render(stdscr, items: list, pos: int, state: dict) -> int:
    h, w = stdscr.getmaxyx()
    stdscr.attron(curses.color_pair(TEXT_PAIR))
    if len(items) == 0:
        stdscr.addstr(0, 1, "No elements, press q to exit")
        return 0
    
    limit = min(h - 2, len(items))
    pos_limit = len(items) // (h - 2) * (h - 2) + len(items) % (h - 2) - limit
    pages = len(items) // limit + (1 if not len(items) % 2 else 0)
    
    def render_line(row: int, item, is_selected: bool):
        prefix = commit_selected if is_selected else commit_not_selected
        if isinstance(item, Commit):
            text = (prefix + commit_render(item))[:w - 1]
        else:
            text = (prefix + ': '.join(item))[:w - 1]  # because it's str
            
        if is_selected:
            stdscr.attron(curses.color_pair(SELECTED_PAIR))
            stdscr.addstr(row, 1, text)
            stdscr.attroff(curses.color_pair(SELECTED_PAIR))
            stdscr.attron(curses.color_pair(TEXT_PAIR))
        else:
            stdscr.addstr(row, 1, text)

    if len(items) <= h - 2:
        for i in range(0, limit):
            render_line(i, items[i], i == (pos % limit))
    else:
        page_num = pos // limit
        for i in range(0, limit):
            item_pos = i + page_num * limit
            if not (item_pos < len(items)):
                break
            render_line(i, items[item_pos], i == (pos % limit))

    stdscr.attroff(curses.color_pair(TEXT_PAIR))
    draw_status_bar(stdscr, pos % limit, state)
    return len(items)

def info_render(stdscr, commit: Commit, pos: int, state: dict) -> int:
    h, w = stdscr.getmaxyx()
    msg = get_text(commit)

    lines = []
    for line in msg.splitlines():
        while len(line) > w - 2:
            lines.append(line[:w - 2])
            line = line[w - 2:]

        if line:
            lines.append(line)
            
    stdscr.attron(curses.color_pair(TEXT_PAIR))

    limit = min(h - 2, len(lines))
    pos_limit = len(lines) // (h - 2) * (h - 2) + len(lines) % (h - 2) - limit

    if len(lines) <= h - 2:
        for i in range(0, limit):
            stdscr.addstr(i, 1, lines[i])
    else:
        for i in range(pos, pos + limit):
            if len(lines) > i:
                stdscr.addstr(i - pos, 1, lines[i % len(lines)])
                
    stdscr.attroff(curses.color_pair(TEXT_PAIR))
    draw_status_bar(stdscr, pos, state)

    return pos_limit

def license_render(stdscr, text: str, pos: int) -> int:
    h, w = stdscr.getmaxyx()

    lines = []
    for line in text.splitlines():
        while len(line) > w - 2:
            lines.append(line[:w - 2])
            line = line[w - 2:]

        if line:
            lines.append(line)
            
    stdscr.attron(curses.color_pair(TEXT_PAIR))

    limit = min(h - 2, len(lines))
    pos_limit = len(lines) // (h - 2) * (h - 2) + len(lines) % (h - 2) - limit

    if len(lines) <= h - 2:
        for i in range(0, limit):
            stdscr.addstr(i, 1, lines[i])
    else:
        for i in range(pos, pos + limit):
            if len(lines) > i:
                stdscr.addstr(i - pos, 1, lines[i % len(lines)])
                
    stdscr.attroff(curses.color_pair(TEXT_PAIR))

    status_bar = f" (q: exit, j/k: navigate) pos: {pos} --license--"
  
    stdscr.attron(curses.color_pair(STATUS_PAIR))
    stdscr.addstr(h - 2, 0, status_bar[:w].ljust(w))
    stdscr.attroff(curses.color_pair(STATUS_PAIR))

    return pos_limit

