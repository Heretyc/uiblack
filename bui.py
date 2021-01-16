from blessed import Terminal
import re

class Bui:
    def __init__(self):
        self.pattern_text = re.compile('([A-Za-z0-9 \-:().`+,!@<>#$%^&*;\\/\|])+')
        self.term = Terminal()
        self.term.enter_fullscreen
        self.height = self.term.height
        self.width = self.term.width

        self.default_bg = f"{self.term.on_black}"
        self.error_bg = f"{self.term.on_white}"
        self.warn_bg = f"{self.term.on_black}"

        self.default_style = f"{self.term.normal}{self.term.white}{self.default_bg}"
        self.error_style = f"{self.term.normal}{self.term.red}{self.error_bg}"
        self.warn_style = f"{self.term.normal}{self.term.yellow}{self.warn_bg}"

    def print(self, text, right=None, down=None):
        if self.term.does_styling:  # Check if output is going into a pipe or other unformatted output
            if (down is not None) and (right is not None):
                with self.term.location():
                    print(self.term.move(down, right) + f"{self.default_style}{text}", end='')
            else:
                print(f"{self.default_style}{text}")
        else:
            print(text)

    def error(self, text):
        if self.term.does_styling:  # Check if output is going into a pipe or other unformatted output
            print(f"{self.error_style}{text}")
        else:
            print(text)

    def warn(self, text):
        if self.term.does_styling:  # Check if output is going into a pipe or other unformatted output
            print(f"{self.warn_style}{text}")
        else:
            print(text)

    def print_center(self, text, style=None, corner=None):
        if style is None:
            style = self.default_style
        if corner is None:
            corner = " "

        center_text = len(text) // 2
        bar = ""

        left_side = (self.width // 2) - (center_text + 4)
        right_side = (self.width // 2) + (center_text + 2)
        top_side = (self.height // 2) - 2
        bottom_side = (self.height // 2) + 2

        for _ in range(0, (len(text) + 6)):
            bar = f"{style}{bar} "

        for y_coord in range(top_side, bottom_side + 1):
            with self.term.location(left_side, y_coord):
                self.print(bar)

        with self.term.location(left_side + 3, top_side + 2):
            self.print(f"{style}{text}")

        if corner != " ":
            with self.term.location(left_side, top_side):
                self.print(f"{style}{corner}")
            with self.term.location(right_side, top_side):
                self.print(f"{style}{corner}")
            with self.term.location(left_side, bottom_side):
                self.print(f"{style}{corner}")
            with self.term.location(right_side, bottom_side):
                self.print(f"{style}{corner}")

    def error_center(self, text):
        self.print_center(text, self.error_style, "!")

    def warn_center(self, text):
        self.print_center(text, self.warn_style, "*")

    def bold(self, text):
        if self.term.does_styling:  # Check if output is going into a pipe or other unformatted output
            return f"{self.term.bold}{text}{self.default_style}"
        else:
            return f"{text}"

    def underline(self, text):
        if self.term.does_styling:  # Check if output is going into a pipe or other unformatted output
            return f"{self.term.underline}{text}{self.term.no_underline}"
        else:
            return f"{text}"

    def clear(self):
        if self.term.does_styling:
            print(self.term.clear())

    def quit(self):
        self.term.exit_fullscreen

    def input(self, question=None, obfuscate=False, max_len=None):
        if max_len is None:
            max_len = self.width - 3
        result = ""
        with self.term.cbreak():
            while True:
                val = ''
                val = self.term.inkey()
                found = self.pattern_text.match(val)
                if val.name == 'KEY_ENTER':
                    break
                elif found is not None:
                    if (len(result) + 1) <= max_len:
                        result = f"{result}{val}"
                    else:
                        continue
                    if obfuscate:
                        self.print("*" * len(result), 2, self.height - 1)
                    else:
                        self.print(result, 2, self.height - 1)

        return result

    def message(self, text, title=""):
        pass

    def set_main_title(self, new_title):
        pass

    def ask_text(self, question):
        pass


    def ask_list(self, question, menu_list):
        self.master.show_menu_popup(question, menu_list, self.change_button_color)

    def ask_yn(self):
        pass

    def test(self):
        result = self.ask_text("question text here")
        self.message(f"result= {result}")


if __name__ == "__main__":
    ui = Bui()
    ui.clear()
    results = ui.input()
    ui.print(f"{ui.bold('some text')} {results}")
    ui.print_center("this is just a test of things")
    ui.warn("warning here")
    ui.error("error here")
    ui.quit()
    ui