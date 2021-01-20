from blessed import Terminal
import re
import datetime

"""uiblack.py: Streamlined cross-platform Textual UI"""

__author__ = "Brandon Blackburn"
__maintainer__ = "Brandon Blackburn"
__email__ = "contact@bhax.net"
__website__ = "https://keybase.io/blackburnhax"
__copyright__ = "Copyright 2021 Brandon Blackburn"
__license__ = "Apache 2.0"

#  Copyright (c) 2021. Brandon Blackburn - https://keybase.io/blackburnhax, Apache License, Version 2.0.
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
#  either express or implied. See the License for the specific
#  language governing permissions and limitations under the License.
#  TL;DR:
#  For a human-readable & fast explanation of the Apache 2.0 license visit:  http://www.tldrlegal.com/l/apache2


class UIBlackTerminal:
    def __init__(self):
        self._title = None
        self._pattern_text = re.compile("([A-Za-z0-9 \-:().`+,!@<>#$%^&*;\\/\|])+")

        self._low_latency_index = 0
        self._low_latency_max = 100

        self.term = Terminal()
        self.term.enter_fullscreen
        self.height = self.term.height
        self.width = self.term.width

        self.default_bg = f"{self.term.on_black}"
        self.window_bg = f"{self.term.reverse}"
        self.error_bg = f"{self.term.on_white}"
        self.warn_bg = f"{self.term.on_black}"

        self.default_style = f"{self.term.normal}{self.term.white}{self.default_bg}"
        self.window_style = f"{self.term.normal}{self.term.white}{self.window_bg}"
        self.error_style = f"{self.term.normal}{self.term.red}{self.error_bg}"
        self.warn_style = f"{self.term.normal}{self.term.yellow}{self.warn_bg}"

        self.update_counter_interval = 100
        self._update_counter = 0
        self._contents_console = []

    def _skip_iteration(self, is_low_latency_enabled):
        # Low latency was set, have we hit max?
        if is_low_latency_enabled:
            if self._low_latency_index >= self._low_latency_max:
                # We hit the max, so run this iteration and reset index
                self._low_latency_index = 0
                return False
            else:
                self._low_latency_index += 1  # Have not hit max, so increment
                return True  # and skip this execution
        return False

    def _check_update(self):
        self._update_counter += 1
        if self._update_counter >= self.update_counter_interval:
            self._update_counter = 0
            self.width = self.term.width
            self.height = self.term.height
            self.clear()
            self._display_main_title()

    def _get_time_string(self):
        now = datetime.datetime.now()
        if self.term.does_styling:
            return f"{self.term.olivedrab}[{self.term.turquoise}{now.strftime('%H:%M')}{self.term.olivedrab}]{self.default_style} "
        else:
            return f"[{now.strftime('%H:%M')}] "

    def print(self, text, right=None, down=None):
        # Check if output is going into a pipe or other unformatted output
        if self.term.does_styling:
            if (down is not None) and (right is not None):
                if down > self.height:
                    down = self.height
                if right > self.width + len(text):
                    right = self.width - len(text)
                if right < 0:
                    right = 0
                if down < 0:
                    down = 0
                with self.term.location():
                    print(
                        self.term.move(down, right) + f"{self.default_style}{text}",
                        end="",
                    )
            else:
                print(f"{self.default_style}{text}")
        else:
            print(text)

    def _clear_console(self):
        total = self.width
        bar = " " * total
        for row in range(1, self.height):
            self.print(bar, 0, row)

    def console(self, text, low_latency=False):
        if self._skip_iteration(low_latency):
            return
        self._contents_console.append(text)
        self._check_update()
        if len(self._contents_console) >= (self.height - 1):
            self._contents_console.pop(0)

        inverse_index = 0
        for index in range(len(self._contents_console) - 1, 0, -1):
            pad = " " * (self.width - len(self._contents_console[index]))
            self.print(
                f"{self._contents_console[index]}{pad}",
                0,
                (self.height - 3) - inverse_index,
            )
            inverse_index += 1

    def notice(self, text):
        # Check if output is going into a pipe or other unformatted output
        if self.term.does_styling:
            self.console(
                f"{self._get_time_string()}{self.default_style}{text}{self.default_style}"
            )
        else:
            print(f"{self._get_time_string()}{text}")

    def info(self, *args):
        self.notice(*args)

    def error(self, text):
        # Check if output is going into a pipe or other unformatted output
        if self.term.does_styling:
            self.console(
                f"{self._get_time_string()}{self.error_style}{text}{self.default_style}"
            )
        else:
            print(f"{self._get_time_string()}{text}")

    def warn(self, text):
        # Check if output is going into a pipe or other unformatted output
        if self.term.does_styling:
            self.console(
                f"{self._get_time_string()}{self.warn_style}{text}{self.default_style}"
            )
        else:
            print(f"{self._get_time_string()}{text}")

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
        if self.term.does_styling:
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
        # Check if output is going into a pipe or other unformatted output
        if self.term.does_styling:
            return f"{self.term.bold}{text}{self.default_style}"
        else:
            return f"{text}"

    def window_text(self, text):
        # Check if output is going into a pipe or other unformatted output
        if self.term.does_styling:
            return f"{self.window_style}{text}{self.default_style}"
        else:
            return f"{text}"

    def underline(self, text):
        # Check if output is going into a pipe or other unformatted output
        if self.term.does_styling:
            return f"{self.term.underline}{text}{self.term.no_underline}"
        else:
            return f"{text}"

    def clear(self):
        if self.term.does_styling:
            print(self.term.clear())
        self._display_main_title()

    def quit(self):
        self.term.exit_fullscreen

    def input(self, question=None, obfuscate=False, max_len=None):
        input_height = self.height - 1
        input_offset = 2

        if question is None:
            question = "Press [Enter] to continue:"
        else:
            # Truncate questions to the length of the terminal window
            question = question[0 : self.width - input_offset]
        self.print(f"{question}", input_offset, input_height - 1)

        if max_len is None:
            max_len = self.width - 3
        result = ""
        with self.term.cbreak():
            while True:
                val = ""
                val = self.term.inkey()
                found = self._pattern_text.match(val)
                if val.name == "KEY_ENTER":
                    break
                elif val.is_sequence:
                    print("got sequence: {0}.".format((str(val), val.name, val.code)))
                elif val.name == "KEY_BACKSPACE" or val.name == "KEY_DELETE":
                    self.print(" " * len(result), input_offset, input_height)
                    result = result[:-1]
                    if obfuscate:
                        self.print("*" * len(result), input_offset, input_height)
                    else:
                        self.print(result, input_offset, input_height)
                elif found is not None:
                    if (len(result) + 1) <= max_len:
                        result = f"{result}{val}"
                    else:
                        continue
                    if obfuscate:
                        self.print("*" * len(result), input_offset, input_height)
                    else:
                        self.print(result, input_offset, input_height)
        self.print(f"{' ' * self.width}", 0, input_height - 1)
        self.print(f"{' ' * self.width}", 0, input_height)

        return result

    def _display_main_title(self):
        if not self.term.does_styling:
            return
        if self._title is None:
            return
        center_text = len(self._title) // 2
        center_screen = self.width // 2
        final_location = center_screen - center_text
        location_tuple = self.term.get_location()
        if location_tuple[0] < 1:
            print("")
            # Moving the console cursor down by one to prevent overwriting title
        self.print(self.window_text(f"{' ' * self.width}"), 0, 0)
        self.print(self.window_text(self._title), final_location, 0)

    def set_main_title(self, new_title):
        if new_title is not None:
            # Truncate titles to the length of the terminal window
            new_title = new_title[0 : self.width]
        self._title = new_title
        self._display_main_title()

    def ask_list(self, question, menu_list):
        menu_height = self.height // 2
        menu_offset = self.width // 2
        menu_top = menu_height - (len(menu_list) + 1)
        # Truncate questions to the length of the terminal window
        question = question[0 : self.width - 2]
        self.print(f"{question}", (menu_offset - len(question)), menu_top - 2)

        index = 0
        for menu_item in menu_list:
            item_offset = menu_offset
            self.print(f"{menu_item}", item_offset, (menu_top + index))
            index += 2

        index = 0
        index_max = len(menu_list) - 1
        with self.term.cbreak():
            while True:
                self.print(
                    f"{self.term.reverse}{menu_list[index]}",
                    menu_offset,
                    (menu_top + (index * 2)),
                )
                val = self.term.inkey()
                if val.name == "KEY_ENTER":
                    break
                elif val.name == "KEY_UP":
                    self.print(
                        f"{menu_list[index]}", menu_offset, (menu_top + (index * 2))
                    )
                    index -= 1
                    if index < 0:
                        index = index_max
                elif val.name == "KEY_DOWN":
                    self.print(
                        f"{menu_list[index]}", menu_offset, (menu_top + (index * 2))
                    )
                    index += 1
                    if index > index_max:
                        index = 0

        return menu_list[index]

        return result

    def _gradient_red_green(self, percent):
        if percent > 100 or percent < 0:
            red = 0
            green = 0
            blue = 100
        else:
            red = 2 * (100 - percent)
            green = 2 * percent
            blue = 0
        if self.term.does_styling:
            return self.term.color_rgb(red, green, blue)
        else:
            return self.default_style

    def load_bar(self, title, iteration, total, low_latency=False, bar_length=50):
        if self._skip_iteration(low_latency):
            return

        if (bar_length + 6) > self.width:
            bar_length = self.width - 6
        bar_left_extent = (self.width // 2) - ((bar_length + 2) // 2)
        bar_upward_extent = self.height // 2
        title_left_extent = (self.width // 2) - ((len(title) + 2) // 2)
        try:
            percent = int(round((iteration / total) * 100))
            fill_len = int(round((bar_length * percent) / 100))
            bar_fill = "█" * fill_len
            bar_empty = " " * (bar_length - fill_len)
            progress_bar = f"{self.warn_style}[{self._gradient_red_green(percent)}{bar_fill + bar_empty}{self.warn_style}]{self.default_style}"
            self.print(f"{title}", title_left_extent, bar_upward_extent - 1)
            for offset in range(0, 3):
                if offset == 1:
                    suffix = f" {percent}%"
                else:
                    suffix = ""
                self.print(
                    f"{progress_bar}{suffix}",
                    bar_left_extent,
                    bar_upward_extent + offset,
                )
        except ZeroDivisionError:
            pass

    def ask_yn(self, question, default_response=False):
        menu_height = self.height // 2
        menu_offset = self.width // 2
        no_offset = menu_offset + 8
        yes_offset = menu_offset - 8
        menu_top = menu_height - 1
        # Truncate questions to the length of the terminal window
        question = question[0 : self.width - 2]
        self.print(f"{question}", (menu_offset - (len(question) // 2)), menu_top - 2)

        self.print("YES", yes_offset, menu_height)
        self.print("NO", no_offset, menu_height)

        index = default_response
        with self.term.cbreak():
            while True:
                if index:
                    self.print(f"{self.term.reverse}YES", yes_offset, menu_height)
                    self.print(f"{self.term.default}NO", no_offset, menu_height)
                else:
                    self.print(f"{self.term.default}YES", yes_offset, menu_height)
                    self.print(f"{self.term.reverse}NO", no_offset, menu_height)
                val = self.term.inkey()
                if val.name == "KEY_ENTER":
                    break
                elif val.name == "KEY_RIGHT" or val == "n":
                    index = False
                elif val.name == "KEY_LEFT" or val == "y":
                    index = True

        return index


if __name__ == "__main__":
    ui = UIBlackTerminal()
    ui.clear()
    ui.error_center("UIBlack should not be run directly.")
    exit(1)
