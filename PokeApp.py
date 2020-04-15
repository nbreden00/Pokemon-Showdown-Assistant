import tkinter as tk
import pokepy
import sys
from PokemonDisplay import PokemonDisplay
from ShowdownListener import ShowdownListener
import json
from EntryAutoFill import EntryAutoFill
from PokemonNameRelations import name_relations


class PokeApp:
    def __init__(self, real_root):
        self.root = real_root
        self.root.title("PokeShowdown Helper")
        self.root.resizable(width=False, height=False)
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.on_exit())

        self.poke_client = pokepy.V2Client()

        # Sets up menu bar at the top of the window
        self.root.menubar = tk.Menu(self.root)
        self.root.config(menu=self.root.menubar)
        self.root.mode_menu = tk.Menu(self.root.menubar, tearoff=0)
        self.root.mode_menu.add_command(label="Manual Lookup Mode", command=lambda: self.switch_modes('one pokemon'))
        self.root.mode_menu.add_command(label="Pokemon Showdown Mode", command=lambda: self.switch_modes('two pokemon'))
        self.root.mode_menu.add_command(label="Toggle Stats", command=lambda: self.toggle_pokemon_stats())
        self.root.mode_menu.add_command(label="Toggle Theme", command=lambda: self.switch_modes('toggle theme'))
        self.root.menubar.add_cascade(label='Options', menu=self.root.mode_menu)

        self.dark_theme = True

        self.current_bg_color = "#3C3F41"  # These are the default colors, same values are in switch_modes
        self.current_fg_color = "#A9B7C6"  # under dark mode.
        self.current_darker_bg_color = "#1a1b1c"

        self.master = tk.Frame(self.root, bg=self.current_bg_color)

        self.master.grid(column=1, row=1)

        self.mode = 'singles'

        # Other variables
        self.showdown_mode = False  # Determines if when the enter button / send button is pressed if the url is
        # updated or if one pokemon is looked up instead

        self.pokemon_stats_shown = True  # Used to show / hide the pokemon stats for all pokemon displays in the
        # self.toggle_pokemon_stats method

        self.pokemon_display_status = {  # Used in creating / destroying pokemon displays and keeping track if they
            1: False,  # exist or not
            2: False
        }

        self.top_bar_frame = tk.Frame(self.master, bg=self.current_bg_color)
        self.top_bar_frame.grid(column=0, row=1, columnspan=3)

        # Input box at the top
        with open("pokemon.json", "r") as file:     # Gets the list of pokemon from pokemon.json for the auto-filling
            self.pokemon_list = json.load(file)

        self.url_input = EntryAutoFill(self.top_bar_frame, self.root, self.pokemon_list, real_width=100,
                                       entry_bg=self.current_fg_color, guess_bg=self.current_fg_color,
                                       max_guesses_shown=4, callback_func=lambda: self.update_url(),
                                       guess_window_bd_color="#000000", guess_window_bd_thickness=1,
                                       cb_if_entry_guess=False, alphabetical=True)

        self.url_input.grid(column=1, row=1)

        # Confirm button to go along input box
        self.url_button = tk.Button(self.top_bar_frame, text="OK", command=self.update_url, fg=self.current_fg_color,
                                    bg=self.current_darker_bg_color, activebackground=self.current_fg_color,
                                    activeforeground="#FFFFFF", takefocus=False)
        self.url_button.grid(column=2, row=1)

        self.loading_icon = None
        self.loading_icon_shown = False

        # Groups used to change the theme
        self.regular_bg_group = [self.master, self.top_bar_frame]
        self.dark_bg_group = [self.url_button]
        self.light_bg_group = [self.url_input]
        self.regular_fg_group = []

        self.pokemon_display_parts = {  # Used to store the  pokemon displays
            1: None,
            2: None
        }

        self.create_pokemon_display(1)

    @staticmethod
    def on_exit():
        """
        Called when window is closed, used to make sure the showdown thread and selenium window close
        :return: None
        """
        global showdown_thread
        showdown_thread.browser.quit()
        showdown_thread.do_stop = True
        sys.exit(0)

    def switch_modes(self, mode):
        """
        Handles most things from the options menu
        :param mode: string Mode to do stuff for
        :return: None
        """
        global showdown_thread
        if mode == 'toggle theme':
            # Switches themes between light and dark mode
            if self.dark_theme:
                bg = "white"
                fg = "black"
                dark_bg = "black"
            else:
                bg = "#3C3F41"  # These colors are the default ones that are in PokeApp class
                fg = "#A9B7C6"
                dark_bg = "#1a1b1c"

            for widget in self.regular_bg_group:
                widget.config(bg=bg)
            for widget in self.dark_bg_group:
                widget.config(bg=dark_bg)
            for widget in self.light_bg_group:
                widget.config(bg=fg)
            for widget in self.regular_fg_group:
                widget.config(fg=fg)

            self.current_bg_color = bg
            self.current_fg_color = fg
            self.current_darker_bg_color = dark_bg

            self.master.config(bg=bg)
            self.root.config(bg=bg)
            self.dark_theme = not self.dark_theme

        elif mode == "one pokemon":
            # Switches to manual lookup mode with one pokemon
            self.url_input.empty()
            self.showdown_mode = False
            showdown_thread.url = ""
            self.url_input.turn_on_guess_window()
            self.delete_pokemon_display(2)

        elif mode == "two pokemon":
            # Switches to pokemon showdown mode where pokemon are updated from given URL
            self.showdown_mode = True
            self.url_input.turn_off_guess_window()
            self.create_pokemon_display(2)

    def show_loading_icon(self):
        """
        Shows loading text if none is already there
        :return: None
        """
        if not self.loading_icon_shown:
            self.loading_icon = tk.Label(self.root, text="LOADING", bg=self.current_bg_color, fg=self.current_fg_color)
            self.loading_icon.place(x=0, y=0)
            self.loading_icon_shown = True
            self.root.update_idletasks()

    def hide_loading_icon(self):
        """
        Hides loading text if there's text to hide
        :return: None
        """
        if self.loading_icon_shown:
            self.loading_icon.destroy()
            self.loading_icon = None
            self.loading_icon_shown = False
            self.root.update_idletasks()

    def update_url(self):
        """
        Updates the url or changes the pokemon shown, depends on what mode is set in self.showdown_mode
        :return: None
        """
        global showdown_thread
        self.show_loading_icon()
        if self.showdown_mode:
            url = self.url_input.get()
            showdown_thread.url = url
            showdown_thread.update_url = True
        else:
            mon = self.url_input.get()
            # Checks if pokemon manually entered is a special one (in PokemonNameRelations.py) if so uses that
            self.pokemon_display_parts[1].change_pokemon(name_relations[mon] if mon in name_relations else mon)
        self.hide_loading_icon()

    def create_pokemon_display(self, number, base_pokemon="darkrai"):
        """
        Creates the pokemon display
        :param number: Number frame to do, number 1-2
        :param base_pokemon: Pokemon to originally display
        :return: None
        """
        if not self.pokemon_display_status[number]:
            self.pokemon_display_parts[number] = PokemonDisplay(self.master, self, self.poke_client, base_pokemon,
                                                                number, bg=self.current_bg_color)
            self.pokemon_display_parts[number].grid(column=1, row=1 + number, sticky='W')
            self.regular_bg_group.append(self.pokemon_display_parts[number])
            self.pokemon_display_status[number] = True
        else:
            pass

    def delete_pokemon_display(self, number):
        """
        Deletes the pokemon display
        :param number: Number frame to do, number 1-2
        :return: None
        """
        if self.pokemon_display_status[number]:
            self.pokemon_display_parts[number].destroy()
            self.pokemon_display_parts[number] = None
            self.pokemon_display_status[number] = False
        else:
            pass

    def toggle_pokemon_stats(self):
        """
        Turns on or off the pokemon stat displays for all PokemonDisplays
        :return: None
        """
        for number in self.pokemon_display_parts:
            try:
                if self.pokemon_stats_shown:
                    self.pokemon_display_parts[number].remove_stat_display()
                else:
                    self.pokemon_display_parts[number].remember_stat_display()
            except AttributeError:
                pass  # Happens if the pokemon display doesn't exist, but is still None type in
                # self.pokemon_display_parts[number]

        self.pokemon_stats_shown = not self.pokemon_stats_shown


if __name__ == "__main__":
    root = tk.Tk()
    gui = PokeApp(root)
    showdown_thread = ShowdownListener(gui)
    showdown_thread.start()
    root.iconbitmap("icon.ico")     # Sets icon here so window only loads when everything is ready
    root.mainloop()
