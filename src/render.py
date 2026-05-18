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

def get_text(commit):
    text = f"""
COMMIT({commit.short_hash})                                              


NAME
       {commit.short_hash} - {commit.subject}

SYNOPSIS
       git show {commit.hash.strip()}

DESCRIPTION
       {commit.body or 'No description provided.'}

AUTHOR
       Name:   {commit.author_name} <{commit.author_email}>
       Date:   {datetime.fromtimestamp(commit.author_ts).strftime("%Y-%m-%d %H:%M:%S")}

COMMITTER
       Name:   {commit.committer_name} <{commit.committer_email}>
       Date:   {datetime.fromtimestamp(commit.committer_ts).strftime("%Y-%m-%d %H:%M:%S")}

REFERENCES
       {', '.join(commit.refs) if commit.refs else 'none'}

PARENTS
{'\n'.join(f'       {p}' for p in commit.parents) if commit.parents else '       none'}

    """
    return text

def commit_render(commit: Commit) -> str:
    return f"{commit.short_hash} - {commit.committer_ts} - {commit.committer_name}"
    
def draw_status_bar(stdscr, dis: int, state: dict) -> None:
    h, w = stdscr.getmaxyx()

    status = state["status"]
    status_bar = f" (q: exit, j/k: navigate, enter: details) pos: {dis} --{status}--"
  
    stdscr.attron(curses.color_pair(STATUS_PAIR))
    stdscr.addstr(h - 2, 0, status_bar[:w].ljust(w))
    stdscr.attroff(curses.color_pair(STATUS_PAIR))

def base_render(stdscr, commits: list[Commit], pos: int, state: dict) -> int:
    h, w = stdscr.getmaxyx()

    stdscr.attron(curses.color_pair(TEXT_PAIR))

    # TODO: Fix it!
    limit = min(h - 2, len(commits))
    pos_limit = len(commits) // (h - 2) * (h - 2) + len(commits) % (h - 2) - limit

    if len(commits) <= h - 2:
        for i in range(0, limit):
             if i == (pos % limit):
                 stdscr.addstr(i, 1, commit_render(commits[i])[:w - 1], curses.A_REVERSE)
             else:
                 stdscr.addstr(i, 1, commit_render(commits[i])[:w - 1])

    else:
        for i in range(pos, pos + limit):
            if len(commits) > i:
                if i == (pos % limit):
                    stdscr.addstr(i - pos, 1, commit_render(commits[i]), curses.A_REVERSE)
                else:
                    stdscr.addstr(i - pos, 1, commit_render(commits[i]))

    stdscr.attroff(curses.color_pair(TEXT_PAIR))
    draw_status_bar(stdscr, pos % limit, state)

    return pos_limit
    
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


