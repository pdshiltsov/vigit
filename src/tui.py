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

def draw_status_bar(stdscr, text: str) -> None:
    h, w = stdscr.getmaxyx()
    y = h - 2

    stdscr.attron(curses.color_pair(STATUS_PAIR))
    stdscr.addstr(y, 0, text[:w].ljust(w))
    stdscr.attroff(curses.color_pair(STATUS_PAIR))


def render(stdscr, info: str) -> None:
    stdscr.erase()

    h, w = stdscr.getmaxyx()

    stdscr.attron(curses.color_pair(TEXT_PAIR))
    stdscr.addstr(2, 2, info)
    stdscr.attroff(curses.color_pair(TEXT_PAIR))

    draw_status_bar(stdscr, " (q to exit)")

    stdscr.refresh()


def main(stdscr) -> None:
    curses.curs_set(0)
    stdscr.keypad(True)

    init_colors()

    y = 0
    while True:
        render(stdscr, f"Hello, world! {y}")

        key = stdscr.getch()

        if key == ord("q"):
            break

        elif key == ord("j"):
            y += 1

        elif key == ord("k"):
            if y - 1 >= 0:
                y -= 1

        else:
            pass # Passing 
            
if __name__ == "__main__":
    curses.wrapper(main)
