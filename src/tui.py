import curses


def main(stdscr):
    stdscr.clear()
    stdscr.addstr(0, 0, "Hello, world!")
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(main)
