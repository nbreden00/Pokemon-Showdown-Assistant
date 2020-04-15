import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import beckett
import Popup


class PokemonDisplay(tk.Frame):
    def __init__(self, parent, app_class, poke_api_class, pokemon='charizard', number=1, **kw):

        self.poke_client = poke_api_class
        self.poke_app = app_class
        self.frame_number = number
        self.parent = parent

        super().__init__(self.parent, **kw)

        self.master = self
        self.current_pokemon = pokemon

        try:
            self.pokemon_data = self.poke_client.get_pokemon(pokemon)
        finally:
            pass

        # Setup the pokemon sprite display
        self.pokemon_sprite_frame = tk.Frame(self.master, bg=self.poke_app.current_bg_color)    # Frame that holds
                                                                                        # pokemon sprite, name, and type
        self.pokemon_sprite_frame.grid(column=1, row=1, sticky=tk.N)

        self.pokemon_render = ImageTk.PhotoImage(Image.open('default.png'))
        self.pokemon_sprite = tk.Label(self.pokemon_sprite_frame, image=self.pokemon_render,  # Label for pokemon sprite
                                       bg=self.poke_app.current_bg_color)
        self.pokemon_sprite.grid(column=1, row=1, columnspan=2)

        self.pokemon_name_label = tk.Label(self.pokemon_sprite_frame, text=self.current_pokemon.capitalize(),
                                           bg=self.poke_app.current_bg_color, fg=self.poke_app.current_fg_color)
        self.pokemon_name_label.grid(column=1, row=0, columnspan=2)

        # Setup weakness and resistance labels
        self.type_frame = tk.Frame(self.master, bg=self.poke_app.current_bg_color)
        self.type_frame.grid(column=3, row=1, sticky=tk.N, rowspan=2)

        self.weaknesses_title = tk.Label(self.type_frame, text="Weak", bg=self.poke_app.current_bg_color,
                                         fg=self.poke_app.current_fg_color)
        self.resistances_title = tk.Label(self.type_frame, text="Resist", bg=self.poke_app.current_bg_color,
                                         fg=self.poke_app.current_fg_color)
        self.immunities_title = tk.Label(self.type_frame, text="Immune", bg=self.poke_app.current_bg_color,
                                         fg=self.poke_app.current_fg_color)
        self.weaknesses_title.grid(column=1, row=1)
        self.resistances_title.grid(column=2, row=1)
        self.immunities_title.grid(column=3, row=1)     # This is also done when immunity types are drawn

        # Sets up variables that are used to display various things
        self.type_one_sprite = None
        self.type_one_render = None     # Needs to be declared b/c Label widget needs a reference to the render always
        self.type_two_sprite = None
        self.type_two_render = None
        self.resistance_labels = []
        self.weakness_labels = []
        self.immunity_labels = []

        # Sets up stuff for stat display
        self.stat_frame = tk.Frame(self.master, bg=self.poke_app.current_bg_color)
        self.stat_frame.grid(column=1, row=2)

        self.stat_bar_width = 100
        self.stat_bar_height = 12
        self.stat_max_value = 150       # Value to determine what stat would fill the stat bar
        self.stat_labels = {
            "HP": None,
            "ATK": None,
            "DEF": None,
            "SPATK": None,
            "SPDEF": None,
            "SPD": None
        }
        self.stat_bar_canvases = {
            "HP": None,
            "ATK": None,
            "DEF": None,
            "SPATK": None,
            "SPDEF": None,
            "SPD": None
        }
        self.stat_bars = {
            "HP": None,
            "ATK": None,
            "DEF": None,
            "SPATK": None,
            "SPDEF": None,
            "SPD": None
        }
        self.stat_value_labels = {
            "HP": None,
            "ATK": None,
            "DEF": None,
            "SPATK": None,
            "SPDEF": None,
            "SPD": None
        }
        self.stat_colors = {
            "HP": "#ff0000",
            "ATK": "#f08030",
            "DEF": "#f8d030",
            "SPATK": "#6890f0",
            "SPDEF": "#78c850",
            "SPD": "#f85888"
        }
        self.create_stat_display()
        self.change_pokemon(pokemon)

        # Adds all widgets to their respective color group in Pokeapp for changing theme
        self.poke_app.regular_bg_group.extend((self.stat_frame, self.pokemon_sprite_frame, self.pokemon_sprite,
                                               self.pokemon_name_label, self.type_frame, self.weaknesses_title,
                                               self.resistances_title, self.immunities_title))
        self.poke_app.regular_fg_group.extend((self.weaknesses_title, self.resistances_title, self.immunities_title,
                                               self.pokemon_name_label))

    def update_sprite(self):
        """
        Updates the current sprite to whatever is set as the current pokemon
        """
        try:
            new_sprite_url = requests.get(self.pokemon_data.sprites.front_default)
            new_sprite_bytes = Image.open(BytesIO(new_sprite_url.content))
            new_sprite = ImageTk.PhotoImage(new_sprite_bytes)
            self.pokemon_sprite.configure(image=new_sprite)
            self.pokemon_sprite.image = new_sprite
        except requests.exceptions.MissingSchema:
            new_sprite = ImageTk.PhotoImage(Image.open('no_picture.png'))
            self.pokemon_sprite.configure(image=new_sprite)
            self.pokemon_sprite.image = new_sprite

    def update_type_relationships(self):
        """
        Updates the type relationships (weaknesses and resistances) for whatever is set as the current pokemon, as
        well as changes the types on display
        """
        # Changes the types on display
        types = self.pokemon_data.types

        try:
            self.poke_app.regular_bg_group.remove(self.type_one_sprite)
        except ValueError:
            pass

        self.type_one_render = ImageTk.PhotoImage(Image.open('type_images/{}.png'.format(str(types[0].type.name))))
        self.type_one_sprite = tk.Label(self.pokemon_sprite_frame, image=self.type_one_render,
                                        bg=self.poke_app.current_bg_color)
        self.type_one_sprite.grid(column=1, row=2)
        self.poke_app.regular_bg_group.append(self.type_one_sprite)

        if len(types) == 2:
            try:
                self.poke_app.regular_bg_group.remove(self.type_two_sprite)
            except ValueError:
                pass
            self.type_two_render = ImageTk.PhotoImage(Image.open('type_images/{}.png'.format(str(types[1].type.name))))
            self.type_two_sprite = tk.Label(self.pokemon_sprite_frame, image=self.type_two_render,
                                            bg=self.poke_app.current_bg_color)
            self.type_two_sprite.grid(column=2, row=2)
            self.poke_app.regular_bg_group.append(self.type_two_sprite)
        else:
            try:
                self.type_two_sprite.grid_forget()
            except AttributeError:
                pass    # Happens when loading a pokemon with one type first, as NoneType can't .grid_forget()

        # Determines the weaknesses, resistances, and immunities
        all_weaknesses = []
        all_resistances = []
        immunities = []
        quad_weaknesses = []
        quad_resistances = []

        for i in range(len(types)):
            for j in self.poke_client.get_type(types[i].type.name).damage_relations.double_damage_from:
                all_weaknesses.append(j.name)
            for k in self.poke_client.get_type(types[i].type.name).damage_relations.half_damage_from:
                all_resistances.append(k.name)
            for l in self.poke_client.get_type(types[i].type.name).damage_relations.no_damage_from:
                immunities.append(l.name)

        weaknesses = [x for x in all_weaknesses if x not in all_resistances]
        resistances = [x for x in all_resistances if x not in all_weaknesses]

        for i in weaknesses:
            if weaknesses.count(i) > 1 and i not in quad_weaknesses:
                quad_weaknesses.append(i)
                weaknesses.remove(i)

        for i in resistances:
            if resistances.count(i) > 1 and i not in quad_resistances:
                quad_resistances.append(i)
                resistances.remove(i)

        for i in immunities:
            if i in weaknesses:
                weaknesses.remove(i)
            if i in resistances:
                resistances.remove(i)

        for i in self.weakness_labels, self.resistance_labels, self.immunity_labels:
            for j in i:
                try:
                    self.poke_app.regular_bg_group.remove(j)
                except ValueError:
                    pass
                j.destroy()

        self.resistance_labels = []
        self.weakness_labels = []
        self.immunity_labels = []

        weaknesses.sort()       # Sorts types alphabetically
        resistances.sort()
        immunities.sort()

        # Creates all the type icons for weaknesses, resistances, and immunities
        self.make_type_icons(weaknesses, quad_weaknesses, self.weakness_labels, 1)
        if len(weaknesses) == 0:
            self.weaknesses_title.grid_remove()
        else:
            self.weaknesses_title.grid()

        self.make_type_icons(resistances, quad_resistances, self.resistance_labels, 2)
        if len(resistances) == 0:
            self.resistances_title.grid_remove()
        else:
            self.resistances_title.grid()

        if len(immunities) > 0:
            self.make_type_icons(immunities, [], self.immunity_labels, 3)
            self.immunities_title.grid(column=3, row=1)
        else:
            self.immunities_title.grid_forget()

    def make_type_icons(self, main_list, quad_list, label_list, column):
        """
        Makes the type icons for weaknesses, resistances, or immunities
        :param main_list: List of all types for group
        :param quad_list: List of quad types for group (quad weaknesses / quad resistances)
        :param label_list: List to add the type labels to
        :param column: Int column to start the labels at
        :return: None
        """
        for i in range(len(main_list)):
            label_image = Image.open('type_images/{}.png'.format(str(main_list[i])))
            label_render = ImageTk.PhotoImage(label_image)
            label = tk.Label(self.type_frame, image=label_render, bg=self.poke_app.current_bg_color)
            if main_list[i] in quad_list:
                label.configure(relief='raised', bd=3, bg='IndianRed1')
            else:
                self.poke_app.regular_bg_group.append(label)
            label.image = label_render
            label.grid(column=column, row=2+i)
            label_list.append(label)

    # noinspection PyTypeChecker
    def create_stat_display(self):
        row = 1     # Initial row for the stat_labels in the self.stat_frame
        for stat in self.stat_labels:
            self.stat_labels[stat] = tk.Label(self.stat_frame, text=stat, bg=self.poke_app.current_bg_color,
                                              fg=self.poke_app.current_fg_color)
            self.stat_labels[stat].grid(column=1, row=row, sticky='W')
            self.poke_app.regular_bg_group.append(self.stat_labels[stat])
            self.poke_app.regular_fg_group.append(self.stat_labels[stat])
            row += 1

        row = 1     # Initial row for the stat_bars in the self.stat_frame
        for stat in self.stat_bar_canvases:
            self.stat_bar_canvases[stat] = tk.Canvas(self.stat_frame, width=self.stat_bar_width,
                                                     height=self.stat_bar_height, bg=self.poke_app.current_fg_color,
                                                     highlightbackground=self.poke_app.current_fg_color)
            self.stat_bar_canvases[stat].grid(column=2, row=row)
            row += 1

        current_stat = 5
        for stat in self.stat_bars:
            # Draws the stat bars in their canvases, these are updated in update_stats to their actual length
            self.stat_bars[stat] = \
                self.stat_bar_canvases[stat].create_rectangle(0, 0, self.stat_bar_width, self.stat_bar_height,
                                                              outline="black", fill=self.stat_colors[stat])
            current_stat -= 1

        current_stat = 5
        row = 1
        for stat in self.stat_value_labels:     # Creates stat value labels next to their canvases
            self.stat_value_labels[stat] = tk.Label(self.stat_frame, text="0", bg=self.poke_app.current_bg_color,
                                                    fg=self.poke_app.current_fg_color)
            self.stat_value_labels[stat].grid(column=3, row=row, sticky='W')
            self.poke_app.regular_bg_group.append(self.stat_value_labels[stat])
            self.poke_app.regular_fg_group.append(self.stat_value_labels[stat])
            current_stat -= 1
            row += 1

    def update_stats(self):
        """
        Updates the stats for whatever is set as the current pokemon
        """
        stats = self.pokemon_data.stats
        current_stat = 5
        for stat in self.stat_bars:
            self.stat_bar_canvases[stat].coords(self.stat_bars[stat], 0, 0,
                                                (stats[current_stat].base_stat / self.stat_max_value) * self.stat_bar_width,
                                                self.stat_bar_height)

            self.stat_value_labels[stat].config(text=str(stats[current_stat].base_stat))
            current_stat -= 1

    def remove_stat_display(self):
        """
        Hides the stat display, all widgets still exist and are updated though
        """
        self.stat_frame.grid_remove()

    def remember_stat_display(self):
        """
        Re-displays the stat display if it isn't shown
        """
        self.stat_frame.grid()

    def change_pokemon(self, pokemon):
        try:
            if "**" in pokemon:     # Used to change type of pokemon (for Arceus, Silvally, and Genesect)
                split_string = pokemon.split("**")
                self.current_pokemon = split_string[0]
                self.pokemon_name_label.config(text=self.current_pokemon.capitalize())
                self.pokemon_data = self.poke_client.get_pokemon(split_string[0])
                self.pokemon_data.types[0].type.name = split_string[1]
                if len(split_string) == 3:
                    self.pokemon_data.types[1].type.name = split_string[2]
                self.update_sprite()
                self.update_type_relationships()
                self.update_stats()
            else:
                self.pokemon_data = self.poke_client.get_pokemon(pokemon)
                self.current_pokemon = pokemon
                self.pokemon_name_label.config(text=self.current_pokemon.capitalize())
                self.update_sprite()
                self.update_type_relationships()
                self.update_stats()
            return True
        except beckett.exceptions.InvalidStatusCodeError:
            # This happpens when an entry that is not in PokeAPI goes through
            Popup.create_popup(self.poke_app.real_root, "That pokemon is not supported",
                               bg=self.poke_app.current_fg_color, window_border_thickness=1,
                               label_bg=self.poke_app.current_fg_color, label_fg="black",
                               button_bg=self.poke_app.current_bg_color, button_fg="white",
                               button_active_bg=self.poke_app.current_fg_color, button_active_fg="black")
