from git_process import Commit
import curses


# TODO: Remove popup windows due to their unstable behaviour
def draw_commit_info_popup(stdscr, commit: Commit):
    h, w = stdscr.getmaxyx()

    height = 10
    width = 40

    max_width = min(60, width - 2)
    msg = commit._msg

    lines = []
    for line in msg.splitlines():
        while len(line) > max_width:
            lines.append(line[:max_width])
            line = line[max_width:]

        if line:
            lines.append(line)

    y = (h - height) // 2
    x = (w - width) // 2

    win = curses.newwin(height, width, y, x)
    win.box()

    # TODO: add pager
    for i in range(0, len(lines)):
        win.addstr(i + 1, 1, lines[i])

    return win
