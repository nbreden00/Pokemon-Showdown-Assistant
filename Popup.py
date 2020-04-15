import tkinter as tk


def create_popup(real_root, msg, **kw):
    popup = Popup(real_root, msg, **kw)
    return popup


class Popup(tk.Frame):
    """
    Creates a popup menu with a message in the center of the root
    -----
    real_root: tk.Tk()
        - The actual root of the tkinter window
    msg: string
        - String to display in the popup
    -----
    label_bg: color
        - Background color of the text
    label_fg: color
        - Foreground color of the text
    button_bg: color
        - Background color of button
    button_fg: color
        - Foreground color of button
    button_active_bg: color
        - Background color of button when pressed
    button_active_fg: color
        - Foreground color of button when pressed
    window_border_color: color
        - Color of the border around the popup
    window_border_thickness: int
        - How thick the border around the popup will be
    """

    def __init__(self, real_root, msg, label_bg="#f0f0f0", label_fg="#000000", button_bg="#f0f0f0", button_fg="#000000",
                 window_border_color="#000000", window_border_thickness=0, button_active_fg="#000000",
                 button_active_bg="#FFFFFF", **kw):

        self.real_root = real_root
        super().__init__(real_root, highlightbackground=window_border_color, highlightthickness=window_border_thickness,
                         **kw)

        self.text_width = 12        # Width of a text character in pixels
        self.text_height = 16

        self.label = tk.Label(self, text=msg, bg=label_bg, fg=label_fg)
        self.label.pack()
        self.button = tk.Button(self, text="Okay.", bg=button_bg, fg=button_fg, command=lambda: self.destroy(),
                                activebackground=button_active_bg, activeforeground=button_active_fg)

        self.button.pack()
        info = self.get_widget_geometry(self.real_root)

        x = (info[0] / 2) - ((self.text_width * len(msg)) / 4)      # Roughly centers the popup in the window
        y = (info[1] / 2) - ((self.text_height * msg.count('\n')) / 2)
        self.place(x=x, y=y)

        self.focus()        # Takes focus so that key presses and focus out will cause popup menu to go away
        self.bind("<Escape>", lambda event: self.destroy())
        self.bind("<Return>", lambda event: self.destroy())
        self.bind("<FocusOut>", lambda event: self.destroy())

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
