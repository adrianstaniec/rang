# Sure, we can sort the file list so that directories appear first and in alphabetical order,
# followed by files in alphabetical order.

import os
import curses
from pathlib import Path


def main(stdscr):
    app = App(stdscr)
    app.run()


class App:
    def __init__(self, stdscr):
        self.screen = stdscr
        self._initialize_screen()
        self.cursor = 0
        self.current_dir = Path(".").absolute()

    def _initialize_screen(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.curs_set(0)

    def refresh_screen(self):
        self.screen.clear()
        self.screen_height, self.screen_width = self.screen.getmaxyx()
        self.col_width = self.screen_width // 2
        self._draw_border()
        self._draw_current_directory()

    def _draw_border(self):
        self.screen.vline(2, self.col_width, "|", self.screen_height)
        self.screen.hline(1, 0, "-", self.screen_width)

    def _draw_current_directory(self):
        self.screen.addstr(0, 0, str(self.current_dir)[: self.col_width])

    def run(self):
        while True:
            self.refresh_screen()
            files = self.get_sorted_files()

            self._draw_file_list(files)
            self._show_selected_file_or_folder_contents(files)

            key = self.screen.getch()
            if key == ord("q"):
                break
            else:
                self.process_key_press(files, key)

    def get_sorted_files(self):
        dirs = sorted(
            [d for d in os.listdir(self.current_dir) if (self.current_dir / d).is_dir()]
        )
        files = sorted(
            [
                f
                for f in os.listdir(self.current_dir)
                if (self.current_dir / f).is_file()
            ]
        )
        return dirs + files

    def _draw_file_list(self, files):
        for idx, filename in enumerate(files):
            self._draw_left(filename, idx, idx == self.cursor)

    def _show_selected_file_or_folder_contents(self, files):
        item = files[self.cursor]
        contents = self._get_file_or_folder_contents(item)

        for i, line in enumerate(contents):
            self._draw_right(line, i)

    def _get_file_or_folder_contents(self, item):
        try:
            with open(self.current_dir / item, "r") as file:
                contents = file.read()
        except IsADirectoryError:
            contents = ", ".join(os.listdir(self.current_dir / item))
        except Exception as e:
            contents = f"Unable to open the file or directory: {e}"

        return contents.split("\n")

    def _draw_right(self, contents, i):
        if 0 <= i + 2 < self.screen_height:
            self.screen.addstr(
                i + 2, self.col_width + 1, contents[: self.col_width - 2]
            )

    def _draw_left(self, text, ypos, color=False):
        if color:
            self.screen.attron(curses.color_pair(1))
        if ypos + 2 < self.screen_height:
            self.screen.addstr(ypos + 2, 0, text[: self.col_width - 1])
        if color:
            self.screen.attroff(curses.color_pair(1))

    def process_key_press(self, files, key):
        if key in [curses.KEY_UP, ord("k")] and self.cursor > 0:
            self.cursor -= 1
        elif key in [curses.KEY_DOWN, ord("j")] and self.cursor < len(files) - 1:
            self.cursor += 1
        elif key == ord("h"):
            self.current_dir = self.current_dir.parent
            self.cursor = 0
        elif key == ord("l"):
            self._try_enter_directory(files)
        elif key == ord("x"):
            self._try_remove_file(files)
        elif key == ord("a"):
            self._try_rename_file(files)
        elif key == curses.KEY_F7:
            self._try_create_directory()

    def _try_enter_directory(self, files):
        try:
            new_path = self.current_dir / files[self.cursor]
            if new_path.is_dir():
                self.current_dir = new_path
                self.cursor = 0
        except Exception as e:
            pass

    def _try_remove_file(self, files):
        try:
            os.remove(self.current_dir / files[self.cursor])
        except Exception as e:
            pass

    def _try_rename_file(self, files):
        new_name = self._ask_user_input("Enter new name: ")
        try:
            os.rename(
                self.current_dir / files[self.cursor], self.current_dir / new_name
            )
        except Exception as e:
            pass

    def _try_create_directory(self):
        new_dir = self._ask_user_input("Enter directory name: ")
        try:
            os.mkdir(self.current_dir / new_dir)
        except Exception as e:
            pass

    def _ask_user_input(self, prompt):
        self.screen.addstr(self.screen_height - 1, 0, prompt)
        curses.echo()
        user_input = self.screen.getstr(self.screen_height - 1, len(prompt), 20).decode(
            "utf-8"
        )
        curses.noecho()
        return user_input


if __name__ == "__main__":
    curses.wrapper(main)