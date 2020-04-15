import tkinter as tk


class EntryAutoFill(tk.Frame):
    """
    An tk.Entry window that provides auto fill suggestions below the entry
    -----
    parent: Parent frame
        - The parent of the entry
    real_root: tk.Tk()
        - The actual root of the tkinter window
    autocomplete_list: list
        - List of entries to look for the autocomplete. Capitalization doesn't matter
    -----
    real_width: int
        - Width of the entry box and guesses
    real_height: int
        - Height of the guesses
    max_guesses_shown: int
        - Max number of guesses shown at one time
    keep_typo_open: boolean
        - Whether the guess window should stay open if the entry text no longer has any correct guesses.
        - This will happen if someone made a typo, if True the window will stay open with the guesses it had in there,
        - False and the window will close.
    entry_take_focus: boolean
        - Whether the TAB key can be pressed to have focus go to entry (True) or not (False)
    selection_bg_color: color
        - Background color of the guesses when one is selected
    selection_fg_color: color
        - Foreground color of the guesses when one is selected
    guess_bg: color
        - Background of the guesses when not selected
    guess_fg: color
        - Foreground of the guesses when not selected
    entry_bg: color
        - Background of the entry widget
    entry_fg: color
        - Foreground of the entry widget
    guess_window_bd_color: color
        - Color for the border around the guess window
    guess_window_bd_thickness: int
        - How thick the border around the guess window will be
    guess_bd_color: color
        - Color for the border around the guess window
    guess_bd_thickness: int
        - How thick the border around the guess window will be
    guess_anchor: (tk.N, tk.NE, tk.E, tk.SE, tk.S, tk.SW, tk.W, tk.NW, or tk.CENTER)
        - Anchor of the guess text
    callback_func: function
        - Function to call when enter is pressed and a complete entry is made
    cb_if_entry_guess: boolean
        - Whether the enter key should always call callback function (False) or if callback function should only be
          called if the entry contains an entry from self.autocomplete_list (True)
    show_guess_window: boolean
        - Whether the guess window should be shown or not
    alphabetical: boolean
        - Whether guesses should appear alphabetically (True) or in order of the given autocomplete_list (False)
    """

    def __init__(self, parent, real_root, autocomplete_list, real_width=100, real_height=19,
                 selection_bg_color="#CCCCFF", selection_fg_color="#000000",
                 max_guesses_shown=4, keep_typo_open=True, guess_bg="#f0f0f0", guess_fg="#000000",
                 entry_bg="#FFFFFF", entry_fg="#000000", guess_anchor=tk.CENTER,
                 callback_func=None, cb_if_entry_guess=True, show_guess_window=True,
                 guess_window_bd_color="#000000", guess_window_bd_thickness=0, guess_bd_color="#000000",
                 guess_bd_thickness=0, entry_take_focus=True, alphabetical=False, **kw):

        self.real_root = real_root
        self.parent = parent
        self.master = self

        self.callback_function = callback_func
        self.callback_if_entry_is_guess = cb_if_entry_guess
        self.keep_window_for_typos = keep_typo_open

        super().__init__(self.parent, **kw)

        self.autocomplete_list = [i.lower() for i in autocomplete_list]
        if alphabetical:
            self.autocomplete_list.sort()

        self.entry_width = real_width  # Defines the length of the entry widget in pixels (also guesses)
        self.entry_height = real_height
        self.entry = tk.Entry(self, width=1, takefocus=entry_take_focus, bg=entry_bg, fg=entry_fg)
        self.stop_characters = [" ", ",", "."]  # Characters that the auto delete will stop at, not deleting them

        # 10 is from the default width of the entry widget, 2 is because ipadx adds length on both sides
        self.entry.pack(ipadx=((self.entry_width - 10) / 2))

        # Binds events to the entry widget
        self.entry.bind("<Key>", lambda event: self.key_pressed(event))
        self.entry.bind("<Tab>", lambda event: self.tab_pressed(event))
        self.entry.bind("<Control-BackSpace>", lambda event: self.ctrl_backspace(event))
        self.entry.bind("<BackSpace>", lambda event: self.back_pressed(event))
        self.entry.bind("<Return>", lambda event: self.enter_pressed(event))
        self.entry.bind("<Up>", lambda event: self.up_arrow_pressed(event))
        self.entry.bind("<Down>", lambda event: self.down_arrow_pressed(event))
        self.entry.bind("<Right>", lambda event: self.right_arrow_pressed(event))
        self.entry.bind("<Delete>", lambda event: self.delete_pressed(event))
        self.entry.bind("<Control-Delete>", lambda event: self.ctrl_delete(event))
        self.entry.bind("<Control-a>", lambda event: self.ctrl_a(event))
        self.entry.bind("<Escape>", lambda event: self.lose_focus())

        # Creates variables used for the guess window
        self.show_guess_window = show_guess_window
        self.current_guesses = []
        self.guess_window_frame = tk.Frame(self.real_root,      # Frame that holds the guess frames and labels
                                           highlightbackground=guess_window_bd_color,
                                           highlightthickness=guess_window_bd_thickness)
        # THIS NEEDS TRUE ROOT ACCESS

        self.guess_label_frames = {}  # Dicts store guess frame and labels so they can be easily accessed by a number
        self.guess_window_labels = {}
        self.max_guesses_shown = max_guesses_shown
        self.guess_anchor = guess_anchor
        self.guess_selected = -1  # Guess selected -1 means no guess is selected, otherwise goes 0 -> max guesses

        self.guess_bg = guess_bg
        self.guess_fg = guess_fg
        self.selection_bg_color = selection_bg_color
        self.selection_fg_color = selection_fg_color

        for i in range(self.max_guesses_shown):  # Creates the guess frames and guess labels
            self.guess_label_frames[i] = tk.Frame(self.guess_window_frame, height=self.entry_height, bg=self.guess_bg,
                                                  width=self.entry_width-(2*guess_window_bd_thickness),
                                                  highlightbackground=guess_bd_color,
                                                  highlightthickness=guess_bd_thickness)
            self.guess_label_frames[i].pack_propagate(0)  # Used so frames are all the same size

            self.guess_window_labels[i] = tk.Label(self.guess_label_frames[i], bg=self.guess_bg,
                                                   anchor=self.guess_anchor)

            # Binds mouse actions to the labels so the mouse can be used to select guesses
            self.guess_window_labels[i].bind("<Enter>", lambda x, c=i: self.highlight_guess(c))
            self.guess_window_labels[i].bind("<Leave>", lambda x, c=i: self.unselect_guesses())
            self.guess_window_labels[i].bind("<Button-1>", lambda x, c=i: (self.select_guess(c),
                                                                           self.fill_with_guess()))

            self.guess_window_labels[i].pack(fill=tk.X)  # fill=tk.X makes the label take up their whole frame
            self.guess_label_frames[i].pack()

    @staticmethod
    def get_widget_geometry(widget):
        """
        Gets the geometry of a widget (width, height, xoffset, yoffset)
        :param widget: Widget to get geometry of
        :return: List of widget's geometry format (width, height, xoffset, yoffset)
        """
        geometry = widget.winfo_geometry()

        def test_if_int(value):
            try:
                dummy_value = int(value)
                return True
            except ValueError:
                return False

        properties = []

        current_string = ""
        for char in geometry:
            if test_if_int(char):
                current_string += char
            else:
                properties.append(int(current_string))
                current_string = ""
        properties.append(int(current_string))
        return properties

    def highlight_guess(self, number):
        """
        Highlights the given guess and un-highlights the others
        :param number: Number guess to highlight
        :return: None
        """
        self.unhighlight_guesses()
        try:
            self.guess_label_frames[number].config(bg=self.selection_bg_color)
            self.guess_window_labels[number].config(bg=self.selection_bg_color, fg=self.selection_fg_color)
        finally:
            pass

    def select_guess(self, number):
        """
        Selects and highlights the given number guess
        :param number: Guess to highlight
        :return: None
        """
        if len(self.current_guesses) > 0 and number <= len(self.current_guesses) and self.show_guess_window:
            self.guess_selected = number
            self.highlight_guess(self.guess_selected)

    def update_guess(self):
        """
        Updates the current guess for item by iterating through all items and comparing them to what is currently
        typed
        :return: True if guess changed, false if guess did not change
        """
        if self.show_guess_window:
            guesses = self.guess_input()
            # Makes sure guess stays the same even if spelling doesn't match but doesn't match any other items either
            # But if entry is empty, as returned by self.guess_input(), then the guesses will be gone
            if guesses == "empty entry":
                self.hide_guess_window()
                self.current_guesses = []
                return False
            elif guesses == "complete entry":
                self.hide_guess_window()
                self.current_guesses = []
                return False
            elif len(guesses) > 0:
                self.current_guesses = guesses
                self.update_guess_window()
                return True
            else:
                if self.keep_window_for_typos:
                    return False
                else:
                    self.unselect_guesses()
                    self.hide_guess_window()

    def unhighlight_guesses(self):
        """
        Un-highlights all guesses
        :return: None
        """
        for i in self.guess_window_labels:
            self.guess_label_frames[i].config(bg=self.guess_bg)
            self.guess_window_labels[i].config(bg=self.guess_bg, fg=self.guess_fg)

    def unselect_guesses(self):
        """
        Un-selects any guess, as well as un-highlights them
        :return: None
        """
        self.unhighlight_guesses()
        self.guess_selected = -1

    def update_guess_window(self):
        """
        Updates the guess window to move to the position of the entry widget as well as have new guesses for what
        is in the entry widget
        :return: None
        """
        # Updates the position of the window
        self.guess_window_frame.place(in_=self.entry, x=-1, y=self.entry_height-1)

        # Updates the text
        display_list = self.current_guesses[:self.max_guesses_shown]  # List of items to be displayed
        count = 0
        for item in display_list:
            self.guess_label_frames[count].pack()
            self.guess_window_labels[count].config(text=item.capitalize(), bg=self.guess_bg, anchor=self.guess_anchor)
            count += 1

        for i in range(self.max_guesses_shown - count):
            self.guess_label_frames[self.max_guesses_shown - 1 - i].pack_forget()

    def hide_guess_window(self):
        """
        Hides the guess window from view
        :return: None
        """
        self.unselect_guesses()
        self.guess_window_frame.place_forget()

    def destroy_guess_window(self):
        """
        Destroys the guess window, this shouldn't be used unless you're done with the entry widget completely
        :return: None
        """
        self.unselect_guesses()
        self.guess_window_frame.destroy()
        self.guess_window_frame = None

    def turn_off_guess_window(self):
        """
        Stops the guess window from appearing and auto-fill from happening
        :return: None
        """
        if self.show_guess_window:
            self.hide_guess_window()
            self.show_guess_window = False

    def turn_on_guess_window(self):
        """
        Turns back on the guess window and starts auto-filling again
        :return: None
        """
        if not self.show_guess_window:
            self.update_guess()
            self.show_guess_window = True

    def guess_input(self):
        """
        Guesses the item based on what is currently typed and iterating through all items
        :return: The guessed item, None if entry doesn't match any items, "empty entry" if entry is empty, "complete
                entry" if the entry matches an item in the autocomplete list
        """
        entry = self.entry.get().lower()  # Gets entry
        if entry == "":
            return "empty entry"
        elif entry in self.autocomplete_list:
            return "complete entry"
        entry_len = len(entry)
        guessed_items = []
        for item in self.autocomplete_list:  # Looks through entire list of items and return the first item that
            if item[:entry_len] == entry:  # matches the current entry
                guessed_items.append(item)

        return guessed_items

    def fill_with_guess(self):
        """
        Fills the entry with self.current_guesses[self.guess_selected]
        :return: None
        """
        def actually_fill_with_guess(main):
            main.entry.delete(0, tk.END)
            main.entry.insert(0, main.current_guesses[main.guess_selected].capitalize())
            main.hide_guess_window()

        if self.entry.get().lower() in self.autocomplete_list:  # If guess entry is full with item name, calls
            self.callback()                                     # self.callback instead of filling out guess
            return

        if self.show_guess_window:
            if self.guess_selected != -1:  # Checks if a guess is selected, -1 means that no selection is made
                actually_fill_with_guess(self)
            elif self.entry.get() in self.current_guesses:  # Checks if entered text is a guess
                actually_fill_with_guess(self)
            elif len(self.current_guesses) == 1:  # Checks if only one guess exists
                actually_fill_with_guess(self)

    def key_pressed(self, event):
        """
        Called when a key is pressed to update guess
        :param event: Key press event. event.char stores the character pressed as a string (a -> "a")
        :return: "break" so that the keys don't type themselves, only this function does
        """
        if event.char != "" and event.state == 0 or event.state == 1:
            try:  # If a selection is made, deletes the selection
                self.entry.delete(self.entry.index("sel.first"), self.entry.index("sel.last"))
            except tk._tkinter.TclError:
                pass
            self.entry.insert(tk.INSERT, event.char)
            self.unselect_guesses()
            self.update_guess()
            self.entry.xview(tk.INSERT)
            return 'break'
        else:
            return

    def tab_pressed(self, event):
        """
        If TAB is pressed, deletes all text in the widget, and replaces it with the current guess
        :param event:
        :return: 'break' so that when TAB is pressed it doesn't select text
        """
        if len(self.current_guesses) > 0:
            new_guess = self.guess_selected + 1
            if new_guess > len(self.current_guesses) - 1 or new_guess >= self.max_guesses_shown:
                new_guess = 0

            self.select_guess(new_guess)

        return 'break'

    def enter_pressed(self, event):
        """
        Called when enter is pressed, fills the entry with a selected guess
        :param event: Event given by self.entry.bind
        :return: None
        """
        if self.show_guess_window:
            if self.callback_if_entry_is_guess:
                self.fill_with_guess()
            elif self.guess_selected == -1:
                self.callback()
            else:
                self.fill_with_guess()
        else:
            self.callback()

    def back_pressed(self, event):
        """
        Functions as normal backspace, is only here so that self.update_guess() can be called
        :param event: Key press event
        :return: 'break' so backspace doesn't delete a word when pressed
        """
        try:  # If a selection is made, deletes the selection
            self.entry.delete(self.entry.index("sel.first"), self.entry.index("sel.last"))
        except tk._tkinter.TclError:  # Else, just backspaces
            self.unselect_guesses()
            self.entry.delete(self.entry.index(tk.INSERT) - 1)
        self.update_guess()
        return 'break'

    def delete_pressed(self, event):
        """
        Makes delete key function normally
        :param event: Event given by self.entry.bind
        :return: 'break' so that the keys don't type themselves, only this function does
        """
        try:  # If a selection is made, deletes the selection
            self.entry.delete(self.entry.index("sel.first"), self.entry.index("sel.last"))
        except tk._tkinter.TclError:  # Else, just deletes
            self.entry.delete(self.entry.index(tk.INSERT))
        self.update_guess()
        return 'break'

    def ctrl_backspace(self, event):
        """
        Deletes the entire word if control-backspace is pressed
        :param event: Key press event
        :return: "break" so that the backspace button doesn't delete a character
        """
        self.unselect_guesses()

        try:  # If a selection is made, deletes the selection
            self.entry.delete(self.entry.index("sel.first"), self.entry.index("sel.last"))
        except tk._tkinter.TclError:
            starting_entry = self.entry.get()
            starting_index = self.entry.index(tk.INSERT) - 1

            for i in self.stop_characters:
                if starting_entry[len(starting_entry) - 1] == i:
                    return  # If the cursor is on a stop_characters, deletes only that character

            deleting = True
            current_index = starting_index
            while deleting:  # Finds the index to stop at, looks for a stop_characters or index 0
                if starting_entry[current_index] not in self.stop_characters and current_index > 0:
                    current_index -= 1
                else:
                    deleting = False

            self.entry.delete(current_index + 1 if current_index > 0 else 0, starting_index + 1)
        self.update_guess()
        return "break"  # Prevents backspace from deleting a key when pressed

    def ctrl_delete(self, event):
        """
        Deletes the entire word if control-backspace is pressed
        :param event: Key press event
        :return: "break" so that the backspace button doesn't delete a character
        """
        self.unselect_guesses()
        try:  # If a selection is made, deletes the selection
            self.entry.delete(self.entry.index("sel.first"), self.entry.index("sel.last"))
        except tk._tkinter.TclError:
            starting_entry = self.entry.get()
            starting_index = self.entry.index(tk.INSERT)

            for i in self.stop_characters:
                if starting_entry[starting_index] == i:
                    return  # If the cursor is on a stop_characters, deletes only that character

            deleting = True
            current_index = starting_index
            while deleting:  # Finds the index to stop at, looks for a stop_characters or the end of the entry box
                if starting_entry[current_index] not in self.stop_characters and current_index < len(starting_entry)-1:
                    current_index += 1
                else:
                    deleting = False

            self.entry.delete(starting_index, current_index if current_index < len(starting_entry)-1 else tk.END)
        self.update_guess()
        return "break"  # Prevents backspace from deleting a key when pressed

    def ctrl_a(self, event):
        """
        Selects all and moves ICURSOR to end
        :param event: Key press event
        :return: None so that it selects all
        """
        self.entry.icursor(tk.END)
        return

    def up_arrow_pressed(self, event):
        """
        Moves the current guess selection up one visually
        :param event: Event given by self.entry.bind
        :return: None
        """
        if len(self.current_guesses) > 0:
            new_guess = self.guess_selected - 1
            if new_guess < 0:
                if len(self.current_guesses) < self.max_guesses_shown:
                    new_guess = len(self.current_guesses)
                else:
                    new_guess = self.max_guesses_shown - 1

            self.select_guess(new_guess)

    def down_arrow_pressed(self, event):
        """
        Moves the current guess selection down one visually
        :param event: Event given by self.entry.bind
        :return: None
        """
        if len(self.current_guesses) > 0:
            new_guess = self.guess_selected + 1
            if new_guess > len(self.current_guesses) - 1 or new_guess >= self.max_guesses_shown:
                new_guess = 0

            self.select_guess(new_guess)

    def right_arrow_pressed(self, event):
        """
        Has to exist so right arrow event doesn't go to self.key_pressed, so the icursor will move normally. Also
        makes guess fill if one is selected
        """
        if self.guess_selected != -1:
            self.fill_with_guess()
            return 'break'
        else:
            pass

    def callback(self):
        """
        Function to call the function given as callback for when ENTER is pressed while in the entry widget
        :return: True if function called, else False
        """
        if self.callback_function is not None:
            self.callback_function()
            return True
        else:
            return False

    def empty(self):
        """
        Deletes all text in the entry box
        :return: None
        """
        self.entry.delete(0, tk.END)

    def get(self):
        """
        Returns the text in self.entry
        :return: String, text currently in text box
        """
        return self.entry.get()

    def lose_focus(self):
        """
        Called when escape is pressed, removes focus from entry and hides guess window
        :return: None
        """
        self.real_root.focus()
        self.hide_guess_window()
