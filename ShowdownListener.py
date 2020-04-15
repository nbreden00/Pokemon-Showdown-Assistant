import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
import time
import threading
from PokemonNameRelations import name_relations


class ShowdownListener(threading.Thread):
    def __init__(self, pokeapp):
        threading.Thread.__init__(self)
        self.do_stop = False
        self.pokeapp = pokeapp
        self.url = None
        options = Options()
        options.headless = True
        self.browser = webdriver.Firefox(options=options)
        self.previous_chat = []
        self.player_one = ""
        self.player_two = ""
        self.player_one_pokemon = ""
        self.player_two_pokemon = ""

        self.update_url = False

    @staticmethod
    def process_name(name):
        if name[-1:] == ")":
            actual_name = name.split(" ")[1][1:-1].lower()  # Gets the string within the parenthesis
            if actual_name in name_relations:
                actual_name = name_relations[actual_name]
            return actual_name
        else:
            actual_name = name.replace(". ", "-") if ". " in name else name.replace(" ",
                                                                                    "-") if " " in name else name
            actual_name = actual_name.lower()
            return name_relations[actual_name] if actual_name in name_relations else actual_name

    def run(self):
        while True:
            if self.do_stop:
                return

            if self.update_url:
                try:
                    self.browser.get(self.url)
                    time.sleep(3)
                except selenium.common.exceptions.InvalidArgumentException:
                    pass
                self.update_url = False

            time.sleep(2)
            if self.pokeapp.showdown_mode and self.url != "":
                chat = self.browser.find_elements_by_class_name("battle-history")
                new_chat = [item for item in chat if item not in self.previous_chat]
                self.previous_chat = chat

                if self.player_one == self.player_two == "":
                    for line in new_chat:
                        line_list = line.text.split(" ")
                        if line_list[0] == "Battle" and line_list[1] == "started":
                            self.player_one = line_list[3]
                            self.player_two = line_list[5][:-1]

                for line in new_chat:
                    line_list = line.text.split(" ")
                    if line_list[0] == "Go!":
                        self.player_one_pokemon = self.process_name(line_list[1][:-1] if len(line_list) == 2 else
                                                                    " ".join(line_list[1:])[:-1])
                        display = self.pokeapp.pokemon_display_parts[1]
                        if display.current_pokemon != self.player_one_pokemon:
                            display.change_pokemon(self.player_one_pokemon)

                    elif line_list[:3] == [self.player_two, "sent", "out"]:
                        self.player_two_pokemon = self.process_name(line_list[3][:-1] if len(line_list) == 4 else
                                                                    " ".join(line_list[3:])[:-1])
                        display = self.pokeapp.pokemon_display_parts[2]
                        if display.current_pokemon != self.player_two_pokemon:
                            display.change_pokemon(self.player_two_pokemon)


