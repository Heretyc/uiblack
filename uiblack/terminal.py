from blessed import Terminal
import re
import datetime
import logging
import logging.handlers
import traceback

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
    def __init__(self, log_name, **kwargs):
        """

        :param log_name: (Required) Name of log file to be written in local directory (Only Alphanumeric chars permitted)
        :type log_name: str
        :keyword restart_log: (bool) Whether the log should be started anew upon each execution
        :keyword log_level: (int) 0 - 7 - Conforms to https://en.wikipedia.org/wiki/Syslog#Severity_level
        :keyword sysloghost: (str) Hostname or IP of Syslog server (Can also be localhost)
        :keyword syslogport: (int) Port of Syslog server, (514 is standard on many systems)
        """
        sysloghost = kwargs.get("sysloghost", None)
        syslogport = kwargs.get("syslogport", None)
        restart_log = kwargs.get("restart_log", True)
        log_level = kwargs.get("log_level", 6)
        if restart_log:
            filemode = "w"
        else:
            filemode = "a"
        if isinstance(log_name, str):
            # Keep only alphanumerics
            self._program_name = re.sub("\W", "", log_name)
            # Truncate name to 50 chars
            self._program_name = self._program_name[0:50]
            self._program_name = self._program_name.lower()
            if len(self._program_name) < 3:
                # Keep only alphanumerics in case __name__ has wierdness
                self._program_name = re.sub("\W", "", __name__).lower()
        else:
            self._program_name = re.sub("\W", "", __name__).lower()

        self._logger = logging.getLogger(self._program_name)
        logging.basicConfig(
            filename=f"{self._program_name}.log",
            filemode=filemode,
            format=f"{self._program_name} - %(levelname)s - %(asctime)s - %(message)s",
            datefmt="%y-%b-%d %H:%M:%S (%z)",
        )
        if isinstance(sysloghost, str) and isinstance(syslogport, int):
            self._logger.addHandler(
                logging.handlers.SysLogHandler(address=(sysloghost, syslogport))
            )
        self.console_a_percentage = 0.75
        self.console_b_percentage = 1 - self.console_a_percentage
        self.set_log_level(log_level)

        self._title = None
        self._pattern_text = re.compile("([ -~])")

        self._low_latency_index = 0
        self._low_latency_max = 100

        self._term = Terminal()
        self._term.enter_fullscreen()
        self._term.hidden_cursor()

        self._default_bg = f"{self._term.on_black}"
        self._window_bg = f"{self._term.reverse}"
        self._error_bg = f"{self._term.on_white}"
        self._warn_bg = f"{self._term.on_black}"

        self._default_style = f"{self._term.normal}{self._term.white}{self._default_bg}"
        self._window_style = f"{self._term.normal}{self._term.white}{self._window_bg}"
        self._error_style = f"{self._term.normal}{self._term.red}{self._error_bg}"
        self._warn_style = f"{self._term.normal}{self._term.yellow}{self._warn_bg}"
        self._default_style = f"{self._term.normal}{self._term.snow3}{self._default_bg}"

        self.update_counter_interval = 100
        self._update_counter = 0
        self.console_scrollback = 500
        self._contents_console_a = [""]
        self._contents_console_b = [""]
        self._previous_height = self._term.height
        self._previous_width = self._term.width

    def set_log_level(self, log_level):
        """
        Sets logging level
        :param log_level: 0 - 7 Conforms to https://en.wikipedia.org/wiki/Syslog#Severity_level
        :type log_level: int
        """
        if log_level == 7:
            self._logger.setLevel(logging.DEBUG)
        elif log_level in [6, 5]:
            self._logger.setLevel(logging.INFO)
        elif log_level == 4:
            self._logger.setLevel(logging.WARNING)
        elif log_level == 3:
            self._logger.setLevel(logging.ERROR)
        elif log_level in [2, 1, 0]:
            self._logger.setLevel(logging.CRITICAL)
        else:
            self._logger.setLevel(logging.NOTSET)

    def _get_dimensions(self, console_letter):
        if console_letter.lower() == "a":
            percentage = self.console_a_percentage
        elif console_letter.lower() == "b":
            percentage = self.console_b_percentage

        width = self._term.width
        height = round(self._term.height * percentage)

        if console_letter.lower() == "a":
            if self._title is None:
                ceiling = 0
            else:
                ceiling = 1
        else:
            ceiling = self._term.height - height

        return width, height, ceiling

    def _horiz_divider_dimensions(self):
        width, height, ceiling = self._get_dimensions("b")
        divider_height = ceiling - 1
        return width, divider_height

    def _draw_divider(self):
        width, divider_height = self._horiz_divider_dimensions()
        text = "═" * width
        self.print(text, 0, divider_height, True)

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

    def _len_printable(self, text):
        return len(self._term.strip(text))

    def _refresh_console(self, console_letter):
        fixed_width, fixed_height, ceiling = self._get_dimensions(console_letter)
        self._draw_divider()
        while len(self._contents_console_a) >= self.console_scrollback:
            self._contents_console_a.pop(0)
        while len(self._contents_console_b) >= self.console_scrollback:
            self._contents_console_b.pop(0)

        self._check_update()

        if console_letter.lower() == "a":
            print_height = fixed_height - 2
            contents = self._contents_console_a
        else:
            print_height = (ceiling + fixed_height) - 1
            contents = self._contents_console_b

        for index in range(len(contents) - 1, 0, -1):
            if print_height < ceiling:
                break
            actual_len = self._len_printable(contents[index])
            pad = " " * (fixed_width - (actual_len + 1))
            if actual_len > fixed_width:
                offset = actual_len - (fixed_width - 5)
                result = f"{contents[index][:-offset]}..."
            else:
                result = contents[index]
            self.print(
                f"{result}{pad}",
                0,
                print_height,
                True,
            )
            print_height -= 1

    def _refresh_consoles(self):
        self._refresh_console("a")
        self._refresh_console("b")

    def _check_update(self):
        self._update_counter += 1
        previous_total = self._previous_height + self._previous_width
        current_total = self._term.height + self._term.width
        if (
            self._update_counter >= self.update_counter_interval
            or current_total != previous_total
        ):
            self._previous_height = self._term.height
            self._previous_width = self._term.width
            self._update_counter = 0
            self.clear()
            self._display_main_title()
            self._refresh_consoles()

    def _get_time_string(self):
        now = datetime.datetime.now()
        if self._term.does_styling:
            return f"{self._term.olivedrab}[{self._term.turquoise}{now.strftime('%H:%M')}{self._term.olivedrab}]{self._default_style} "
        else:
            return f"[{now.strftime('%H:%M')}] "

    def print(self, text, right=None, down=None, ignore_log=False):
        """
        Prints normally, or prints to a specified X,Y coordinate on screen.
        Optionally, can ignore logging of text.
        :param text: Text to be written on screen
        :type text: str
        :param right: X coordinate on screen
        :type right: int
        :param down: Y coordinate on screen
        :type down: int
        :param ignore_log: Prevent logging of the text
        :type ignore_log: bool
        """
        if not ignore_log:
            self._logger.info(text)
        # Check if output is going into a pipe or other unformatted output
        if self._term.does_styling:
            actual_len = self._len_printable(text)
            if (down is not None) and (right is not None):
                if down > self._term.height:
                    # Since all the text will not be displayable, skip
                    return
                if right > self._term.width:
                    return
                if right + actual_len > self._term.width:
                    # Truncate the string to prevent wraparound
                    # We take off the right side of the string to deal with formatting non-printables being on the left
                    offset = self._term.width - right
                    trim = actual_len - offset
                    if trim < 1:
                        return
                    text = f"{text[:-trim]}"
                if right < 0:
                    return
                if down < 0:
                    return
                with self._term.location():
                    print(
                        self._term.move(down, right) + f"{self._default_style}{text}",
                        end="",
                    )
            else:
                print(f"{self._default_style}{text}")
        else:
            print(text)

    def _clear_console(self):
        bar = " " * self._term.width
        for row in range(1, self._term.height):
            self.print(bar, 0, row, True)

    def console(self, text, low_latency=False, ignore_log=False, **kwargs):
        """
        Write text to the virtual console similar to standard lib print()
        :param text: Text to be printed
        :type text: str
        :param low_latency: Save text, but only print every 100 iterations to reduce latency
        :type low_latency: bool
        :param ignore_log: Do not log text
        :type ignore_log: bool
        :return:
        """
        if not ignore_log and not low_latency:
            self._logger.info(text)
        elif not ignore_log and low_latency:
            self._logger.debug(text)

        console = kwargs.get("console", "a")
        if console == "a":
            self._contents_console_a.append(text)
            while len(self._contents_console_a) >= self.console_scrollback:
                self._contents_console_a.pop(0)
        elif console == "b":
            self._contents_console_b.append(text)
            while len(self._contents_console_b) >= self.console_scrollback:
                self._contents_console_b.pop(0)

        if self._skip_iteration(low_latency):
            return

        self._refresh_consoles()

    def notice(self, text, **kwargs):
        self._logger.info(text)
        if not self._logger.level <= logging.INFO:
            return
        # Check if output is going into a pipe or other unformatted output
        if self._term.does_styling:
            self.console(
                f"{self._get_time_string()}{self._default_style}{text}",
                False,
                True,
                **kwargs,
            )
        else:
            print(f"{self._get_time_string()}{text}")

    def info(self, *args, **kwargs):
        self.notice(*args, **kwargs)

    def debug(self, text, **kwargs):
        self._logger.debug(text)
        if not self._logger.level <= logging.DEBUG:
            return
        # Check if output is going into a pipe or other unformatted output
        if self._term.does_styling:
            self.console(
                f"{self._get_time_string()}{self._default_style}{text}",
                False,
                True,
                **kwargs,
            )
        else:
            print(f"{self._get_time_string()}{text}")

    def error(self, text, **kwargs):
        self._logger.error(text)
        if not self._logger.level <= logging.ERROR:
            return
        # Check if output is going into a pipe or other unformatted output
        if self._term.does_styling:
            self.console(
                f"{self._get_time_string()}{self._error_style}{text}",
                False,
                True,
                **kwargs,
            )
        else:
            print(f"{self._get_time_string()}{text}")

    def warn(self, text, **kwargs):
        self._logger.warning(text)
        if not self._logger.level <= logging.WARNING:
            return
        # Check if output is going into a pipe or other unformatted output
        if self._term.does_styling:
            self.console(
                f"{self._get_time_string()}{self._warn_style}{text}",
                False,
                True,
                **kwargs,
            )
        else:
            print(f"{self._get_time_string()}{text}")

    def print_center(self, text, style=None, corner=None, ignore_logging=False):
        self._check_update()
        if not ignore_logging:
            self._logger.info(text)
        if style is None:
            style = self._default_style
        if corner is None:
            corner = " "

        center_text = len(text) // 2
        bar = ""

        left_side = (self._term.width // 2) - (center_text + 4)
        right_side = (self._term.width // 2) + (center_text + 2)
        top_side = (self._term.height // 2) - 2
        bottom_side = (self._term.height // 2) + 2

        for _ in range(0, (len(text) + 6)):
            bar = f"{style}{bar} "

        for y_coord in range(top_side, bottom_side + 1):
            self.print(bar, left_side, y_coord, True)

        self.print(f"{style}{text}", left_side + 3, top_side + 2, True)
        if self._term.does_styling:
            if corner != " ":
                self.print(f"{style}{corner}", left_side, top_side, True)
                self.print(f"{style}{corner}", right_side, top_side, True)
                self.print(f"{style}{corner}", left_side, bottom_side, True)
                self.print(f"{style}{corner}", right_side, bottom_side, True)

    def error_center(self, text):
        self._logger.error(text)
        if self._logger.level >= logging.ERROR:
            return
        self.print_center(text, self._error_style, "!", True)

    def warn_center(self, text):
        self._logger.warning(text)
        if self._logger.level >= logging.WARNING:
            return
        self.print_center(text, self._warn_style, "*", True)

    def bold(self, text):
        # Check if output is going into a pipe or other unformatted output
        if self._term.does_styling:
            return f"{self._term.bold}{text}"
        else:
            return f"{text}"

    def window_text(self, text):
        # Check if output is going into a pipe or other unformatted output
        if self._term.does_styling:
            return f"{self._window_style}{text}"
        else:
            return f"{text}"

    def underline(self, text):
        # Check if output is going into a pipe or other unformatted output
        if self._term.does_styling:
            return f"{self._term.underline}{text}{self._term.no_underline}"
        else:
            return f"{text}"

    def clear(self):
        if self._term.does_styling:
            print(self._term.clear())
            self._display_main_title()

    def quit(self):
        self._term.exit_fullscreen

    def input(self, question=None, obfuscate=False, max_len=None):
        self._refresh_consoles()
        input_height = self._term.height - 1
        input_offset = 2

        if question is None:
            question = "Press [Enter] to continue:"
        else:
            # Truncate questions to the length of the terminal window
            question = question[0 : self._term.width - input_offset]
        self._logger.debug(question)
        self.print(f"{question}", input_offset, input_height - 1, True)

        if max_len is None:
            max_len = self._term.width - 3
        result = ""
        with self._term.cbreak():
            while True:
                val = ""
                val = self._term.inkey()
                found = self._pattern_text.match(val)
                if val.name == "KEY_ENTER":
                    break
                elif val.is_sequence:
                    print("got sequence: {0}.".format((str(val), val.name, val.code)))
                elif val.name == "KEY_BACKSPACE" or val.name == "KEY_DELETE":
                    self.print(" " * len(result), input_offset, input_height, True)
                    result = result[:-1]
                    if obfuscate:
                        self.print("*" * len(result), input_offset, input_height, True)
                    else:
                        self.print(result, input_offset, input_height, True)
                elif found is not None:
                    if (len(result) + 1) <= max_len:
                        result = f"{result}{val}"
                    else:
                        continue
                    if obfuscate:
                        self.print("*" * len(result), input_offset, input_height, True)
                    else:
                        self.print(result, input_offset, input_height, True)
        self.print(f"{' ' * self._term.width}", 0, input_height - 1, True)
        self.print(f"{' ' * self._term.width}", 0, input_height, True)

        return result

    def _display_main_title(self):
        if not self._term.does_styling:
            return
        if self._title is None:
            return
        center_text = len(self._title) // 2
        center_screen = self._term.width // 2
        final_location = center_screen - center_text
        location_tuple = self._term.get_location()
        if location_tuple[0] < 1:
            print("")
            # Moving the console cursor down by one to prevent overwriting title
        self.print(self.window_text(f"{' ' * self._term.width}"), 0, 0, True)
        self.print(self.window_text(self._title), final_location, 0, True)

    def set_main_title(self, new_title):
        if new_title is not None:
            # Truncate titles to the length of the terminal window
            new_title = new_title[0 : self._term.width]
        self._title = new_title
        self._logger.info(self._title)
        self._display_main_title()

    def ask_list(self, question, menu_list):
        self._refresh_consoles()
        self._logger.debug(question)
        menu_height = self._term.height // 2
        menu_offset = self._term.width // 2
        menu_top = menu_height - (len(menu_list) + 1)
        # Truncate questions to the length of the terminal window
        question = question[0 : self._term.width - 2]
        self.print(f"{question}", (menu_offset - len(question)), menu_top - 2)

        index = 0
        for menu_item in menu_list:
            item_offset = menu_offset
            self.print(f"{menu_item}", item_offset, (menu_top + index), True)
            index += 2

        index = 0
        index_max = len(menu_list) - 1
        with self._term.cbreak():
            while True:
                self.print(
                    f"{self._term.reverse}{menu_list[index]}",
                    menu_offset,
                    (menu_top + (index * 2)),
                    True,
                )
                val = self._term.inkey()
                if val.name == "KEY_ENTER":
                    break
                elif val.name == "KEY_UP":
                    self.print(
                        f"{menu_list[index]}",
                        menu_offset,
                        (menu_top + (index * 2)),
                        True,
                    )
                    index -= 1
                    if index < 0:
                        index = index_max
                elif val.name == "KEY_DOWN":
                    self.print(
                        f"{menu_list[index]}",
                        menu_offset,
                        (menu_top + (index * 2)),
                        True,
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
        if self._term.does_styling:
            return self._term.color_rgb(red, green, blue)
        else:
            return self._default_style

    def load_bar(self, title, iteration, total, low_latency=False, bar_length=50):
        self._logger.debug(title)
        if self._skip_iteration(low_latency):
            return
        self._check_update()
        if (bar_length + 6) > self._term.width:
            bar_length = self._term.width - 6
        bar_left_extent = (self._term.width // 2) - ((bar_length + 2) // 2)
        bar_upward_extent = self._term.height // 2
        title_left_extent = (self._term.width // 2) - ((len(title) + 2) // 2)
        try:
            percent = int(round((iteration / total) * 100))
            fill_len = int(round((bar_length * percent) / 100))
            bar_fill = "█" * fill_len
            bar_empty = " " * (bar_length - fill_len)
            progress_bar = f"{self._warn_style}[{self._gradient_red_green(percent)}{bar_fill + bar_empty}{self._warn_style}]{self._default_style}"
            self.print(" " * bar_length, bar_left_extent, bar_upward_extent - 1, True)
            self.print(f"{title}", title_left_extent, bar_upward_extent - 1, True)
            for offset in range(0, 3):
                if offset == 1:
                    suffix = f" {percent}%"
                else:
                    suffix = ""
                self.print(
                    f"{progress_bar}{suffix}",
                    bar_left_extent,
                    bar_upward_extent + offset,
                    True,
                )
        except ZeroDivisionError:
            pass

    def ask_yn(self, question, default_response=False):
        self._logger.debug(question)
        self._refresh_consoles()
        menu_height = self._term.height // 2
        menu_offset = self._term.width // 2
        no_offset = menu_offset + 8
        yes_offset = menu_offset - 8
        menu_top = menu_height - 1
        # Truncate questions to the length of the terminal window
        question = question[0 : self._term.width - 2]
        self.print(
            f"{question}", (menu_offset - (len(question) // 2)), menu_top - 2, True
        )

        self.print("YES", yes_offset, menu_height, True)
        self.print("NO", no_offset, menu_height, True)

        index = default_response
        with self._term.cbreak():
            while True:
                if index:
                    self.print(
                        f"{self._term.reverse}YES", yes_offset, menu_height, True
                    )
                    self.print(f"{self._term.default}NO", no_offset, menu_height, True)
                else:
                    self.print(
                        f"{self._term.default}YES", yes_offset, menu_height, True
                    )
                    self.print(f"{self._term.reverse}NO", no_offset, menu_height, True)
                val = self._term.inkey()
                if val.name == "KEY_ENTER":
                    break
                elif val.name == "KEY_RIGHT" or val == "n":
                    index = False
                elif val.name == "KEY_LEFT" or val == "y":
                    index = True

        return index

    def wrapper(self, func: object) -> object:
        """
        Use the following example in your own code:
        from uiblack.terminal import UIBlackTerminal
        ui = UIBlackTerminal()

        @ui.wrapper  # Notice the function is wrapped using "pie" syntax before each function
        def badfunc():
            raise KeyError

        :param func: function object
        :type func: object
        :return: wrapped function call, safe from exceptions, but all of them logged
        """

        def function_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                trace = traceback.format_exc(limit=-1).replace("\n", " >> ")
                # Yes, I could have used self_logger.exception(), but this way ensures a single line output on the log
                console = kwargs.get("console", "a")
                self.error(f"Exception: {trace}", console=console)
                self._refresh_consoles()

        return function_wrapper


if __name__ == "__main__":
    ui = UIBlackTerminal("error")
    ui.clear()
    ui.error_center("UIBlack should not be run directly.")
    exit(1)
