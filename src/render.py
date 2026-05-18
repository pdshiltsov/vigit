# Copyright (C) 2025 vigit
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.

import curses
from git_process import Commit
from config import *


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
       Date:   {commit.author_ts}

COMMITTER
       Name:   {commit.committer_name} <{commit.committer_email}>
       Date:   {commit.committer_ts}

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
    y = h - 2

    status = state["status"]
    status_bar = f" (q to exit) pos: {dis}, h: {h}, w: {w} --{status}--"
  
    stdscr.attron(curses.color_pair(STATUS_PAIR))
    stdscr.addstr(y, 0, status_bar[:w].ljust(w))
    stdscr.attroff(curses.color_pair(STATUS_PAIR))

def base_render(stdscr, commits: list[Commit], pos: int, state: dict) -> None:
    h, w = stdscr.getmaxyx()

    stdscr.attron(curses.color_pair(TEXT_PAIR))

    limit = min(h - 2, len(commits))
    pos_limit = len(commits) // (h - 2) * (h - 2) + len(commits) % (h - 2) - limit

    if len(commits) <= h - 2:
        for i in range(0, limit):
             if i == (pos % limit):
                 stdscr.addstr(i, 1, commit_render(commits[i % len(commits)])[:w - 1], curses.A_REVERSE)
             else:
                 stdscr.addstr(i, 1, commit_render(commits[i % len(commits)])[:w - 1])

    else:
        if pos > pos_limit:
            pos = pos_limit
        
        for i in range(pos, pos + limit):
            if len(commits) > i:
                if i == (pos % limit):
                    stdscr.addstr(i, 1, commit_render(commits[i % len(commits)]), curses.A_REVERSE)
                else:
                    stdscr.addstr(i, 1, commit_render(commits[i % len(commits)]))

    stdscr.attroff(curses.color_pair(TEXT_PAIR))
    draw_status_bar(stdscr, pos % limit, state)

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
        if pos > pos_limit:
            pos = pos_limit
        
        for i in range(pos, pos + limit):
            if len(lines) > i:
                stdscr.addstr(i - pos, 1, lines[i % len(lines)])
    
    stdscr.attroff(curses.color_pair(TEXT_PAIR))
    draw_status_bar(stdscr, pos, state)

    return pos_limit
