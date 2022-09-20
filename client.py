from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from rich.pretty import pprint


class Client:
    def __init__(self):
        pass
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        driver.get("https://www.chess.com/login_and_go?returnUrl=https://www.chess.com/play/online/friend")
        driver.implicitly_wait(10)

        self._game_started = False
        self._driver = driver
        self._castling_rights = "QKqk"

        # login
        username_field = self._driver.find_element(By.CSS_SELECTOR, "#username")
        password_field = self._driver.find_element(By.CSS_SELECTOR, "#password")

        username_field.send_keys("edw0006gwsc.vic.edu.au@gmail.com")
        password_field.send_keys("Paddy2002")

        self._driver.find_element(By.CSS_SELECTOR, "#login").click()

        # block until game is started
        while True:
            try:
                self._driver.find_element(By.CSS_SELECTOR, ".clock-player-turn")
                self._game_started = True
                board = self._driver.find_element(By.CSS_SELECTOR, ".board")
                self._player_colour = "b" if "flipped" in board.get_attribute("class") else "w"
                break
            except NoSuchElementException:
                continue

    def get_game_ready(self):
        return self._game_started

    def get_player_colour(self):
        return self._player_colour

    def move(self, start, end):
        # pieces are defined as "square-{column}{row}"
        # eg c3 - square-31
        pass

    def get_fen(self):
        # get .board and get all child elements
        # get there piece locations; and generate fen

        # generate piece list
        pieces_DOM_elements = self._driver.find_elements(By.CSS_SELECTOR, ".board .piece")
        piece_list = []
        for piece in pieces_DOM_elements:
            class_name = piece.get_attribute("class").split(" ")
            location = class_name[-1][-2::]
            piece_type = class_name[1][1]
            piece_colour = class_name[1][0]
            piece_info = { 
                "type": piece_type,
                "colour": piece_colour,
                "location": location
            }
            piece_list.append(piece_info)

        piece_list.sort(key=lambda piece:int(piece["location"][0])) #sort left to right
        piece_list.sort(key=lambda piece:int(piece["location"][1]), reverse=True) #sort by rank

        # piece_list = [{'type': 'r', 'colour': 'b', 'location': '18'}, {'type': 'n', 'colour': 'b', 'location': '28'}, {'type': 'b', 'colour': 'b', 'location': '38'}, {'type': 'q', 'colour': 'b', 'location': '48'}, {'type': 'k', 'colour': 'b', 'location': '58'}, {'type': 'b', 'colour': 'b', 'location': '68'}, {'type': 'n', 'colour': 'b', 'location': '78'}, {'type': 'r', 'colour': 'b', 'location': '88'}, {'type': 'p', 'colour': 'b', 'location': '17'}, {'type': 'p', 'colour': 'b', 'location': '27'}, {'type': 'p', 'colour': 'b', 'location': '37'}, {'type': 'p', 'colour': 'b', 'location': '47'}, {'type': 'p', 'colour': 'b', 'location': '67'}, {'type': 'p', 'colour': 'b', 'location': '77'}, {'type': 'p', 'colour': 'b', 'location': '55'}, {'type': 'p', 'colour': 'b', 'location': '85'}, {'type': 'p', 'colour': 'w', 'location': '54'}, {'type': 'p', 'colour': 'w', 'location': '84'}, {'type': 'r', 'colour': 'w', 'location': '83'}, {'type': 'p', 'colour': 'w', 'location': '12'}, {'type': 'p', 'colour': 'w', 'location': '22'}, {'type': 'p', 'colour': 'w', 'location': '32'}, {'type': 'p', 'colour': 'w', 'location': '42'}, {'type': 'p', 'colour': 'w', 'location': '62'}, {'type': 'p', 'colour': 'w', 'location': '72'}, {'type': 'r', 'colour': 'w', 'location': '11'}, {'type': 'n', 'colour': 'w', 'location': '21'}, {'type': 'b', 'colour': 'w', 'location': '31'}, {'type': 'q', 'colour': 'w', 'location': '41'}, {'type': 'k', 'colour': 'w', 'location': '51'}, {'type': 'b', 'colour': 'w', 'location': '61'}, {'type': 'n', 'colour': 'w', 'location': '71'}]
        
        pprint(piece_list)
        # set blank piece at the end to signify there is no more pieces left
        piece_list.append({
            "type": "",
            "colour": "",
            "location": ""
        })
        self._castling_rights = "QKqk"
        self._player_colour = "w"
        fen = ""
        blank_squares_counter = 0
        i = 0
        for rank in range(8, 0, -1):
            for file in range(1, 9):

                # check for castling rights
                if piece_list[i]["type"] == "k":
                    if piece_list[i]["colour"] == "w" and piece_list[i]["location"] != "51":
                        self._castling_rights = self._castling_rights.replace("QK", "")
                    elif piece_list[i]["colour"] == "b" and piece_list[i]["location"] != "58":
                        self._castling_rights = self._castling_rights.replace("qk", "")
                
                if piece_list[i]["type"] != "r" or piece_list[i]["location"] != str(file) + str(rank):
                    if rank == 1:
                        if file == 1:
                            self._castling_rights = self._castling_rights.replace("Q", "")
                        elif file == 8:
                            self._castling_rights = self._castling_rights.replace("K", "")
                    if rank == 8:
                        if file == 1:
                            self._castling_rights = self._castling_rights.replace("q", "")
                        elif file == 8:
                            self._castling_rights = self._castling_rights.replace("k", "")

                # check if there is a piece on the location
                if piece_list[i]["location"] == str(file) + str(rank):
                    if blank_squares_counter > 0:
                        fen += str(blank_squares_counter)
                    blank_squares_counter = 0

                    letter = piece_list[i]["type"]
                    if piece_list[i]["colour"] == "w":
                        letter = letter.upper()
                    fen += letter
                    i += 1
                else:
                    blank_squares_counter += 1

            if blank_squares_counter > 0:
                fen += str(blank_squares_counter)
            blank_squares_counter = 0
            if rank != 1:
                fen += "/"

        fen += " "
        fen += self._player_colour
        if self._castling_rights:
            fen += f" {self._castling_rights}"
        else:
            fen += " -"

        fen += " - 0 1"
        pprint(fen)
        return fen

    def wait_for_turn(self):
        while True:
            try:
                self._driver.find_element(By.CSS_SELECTOR, ".board-layout-bottom .clock-player-turn")
                return True
            except NoSuchElementException:
                continue


client = Client()

while True:
    client.wait_for_turn()
    client.get_fen()
    sleep(10)