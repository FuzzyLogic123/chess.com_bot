
from enum import auto
from time import sleep
import chime
from rich.pretty import pprint
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver import ActionChains

chime.theme("big-sur")

class Client:
    def __init__(self):
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        driver.get("https://www.chess.com/login_and_go?returnUrl=https://www.chess.com/play/online/new")
        # driver.implicitly_wait(10)

        self._game_started = False
        self._waiting_for_new_game = True
        self._driver = driver

        # login
        username_field = self._driver.find_element(By.CSS_SELECTOR, "#username")
        password_field = self._driver.find_element(By.CSS_SELECTOR, "#password")

        username_field.send_keys("PhillDunphey")
        password_field.send_keys("Paddy2002")
        self._driver.find_element(By.CSS_SELECTOR, "#login").click()

        self.start_new_game()

    def get_game_ready(self):
        return self._game_started

    def get_player_colour(self):
        return self._player_colour

    def get_time_remaining(self):
        clock = self._driver.find_element(By.CSS_SELECTOR, ".player-bottom .clock-component")
        time_in_ms = 0
        time_remaining = clock.text
        [minutes, seconds] = time_remaining.split(":")

        time_in_ms += int(minutes) * 1000 * 60

        if "." in seconds:
            [seconds, ms] = seconds.split(".")
            time_in_ms += int(ms) * 100
        time_in_ms += int(seconds) * 1000
        self._time_remaining = time_in_ms
        return time_in_ms

    def move(self, stockfish_reccomendation):
        # chime.warning(True)
        move_chesscom_notation = "".join([str(ord(char.lower()) - 96) if i % 2 == 0 else char for i, char in enumerate(stockfish_reccomendation)])
        start = move_chesscom_notation[:2]
        end = move_chesscom_notation[2:4]
        start_end = [start, end]

        # if you're black - reverse the board aka 9 - square number
        if self._player_colour == "b":
            for i in range(len(start_end)):
                tmp = ""
                for char in start_end[i]:
                    tmp += str(9 - int(char))
                start_end[i] = tmp

        start = start_end[0]
        end = start_end[1]
        # calculate square size bounding box for square, then multiply that with the coordinate + 0.5 + bounding box of the board
        piece_dimensions = self._driver.find_element(By.CSS_SELECTOR, ".piece").rect
        board_dimensions = self._driver.find_element(By.CSS_SELECTOR, ".board").rect

        square_width = piece_dimensions["width"]
        x_offset = board_dimensions["x"]
        y_offset = board_dimensions["y"] + board_dimensions["height"]

        client_x_start = square_width * (int(start[0]) - 1 + 0.5) + x_offset
        client_y_start = - square_width * (int(start[1]) - 1 + 0.5) + y_offset
        client_x_end = square_width * (int(end[0]) - 1 + 0.5) + x_offset
        client_y_end = - square_width * (int(end[1]) - 1 + 0.5) + y_offset


        self._driver.execute_script(f"""
            const pe = new PointerEvent("pointerdown", {{ bubbles: true, cancelable: true, view: window, clientX: {client_x_start}, clientY: {client_y_start} }});
            document.querySelector(".board").dispatchEvent(pe)
            const peu = new PointerEvent("pointerup", {{ bubbles: true, cancelable: true, view: window, clientX: {client_x_end}, clientY: {client_y_end} }});
            document.querySelector(".board").dispatchEvent(peu)
        """)

            # move to location
            # action_builder.pointer_action.move_to_location(client_x, client_y)
            # action_builder.pointer_action.click()
            # action_builder.perform()


    def get_fen(self):
        # get .board and get all child elements
        # get there piece locations; and generate fen
        piece_list = self.get_piece_list()
        # piece_list = [{'type': 'r', 'colour': 'b', 'location': '18'}, {'type': 'n', 'colour': 'b', 'location': '28'}, {'type': 'b', 'colour': 'b', 'location': '38'}, {'type': 'q', 'colour': 'b', 'location': '48'}, {'type': 'k', 'colour': 'b', 'location': '58'}, {'type': 'b', 'colour': 'b', 'location': '68'}, {'type': 'n', 'colour': 'b', 'location': '78'}, {'type': 'r', 'colour': 'b', 'location': '88'}, {'type': 'p', 'colour': 'b', 'location': '17'}, {'type': 'p', 'colour': 'b', 'location': '27'}, {'type': 'p', 'colour': 'b', 'location': '37'}, {'type': 'p', 'colour': 'b', 'location': '47'}, {'type': 'p', 'colour': 'b', 'location': '67'}, {'type': 'p', 'colour': 'b', 'location': '77'}, {'type': 'p', 'colour': 'b', 'location': '55'}, {'type': 'p', 'colour': 'b', 'location': '85'}, {'type': 'p', 'colour': 'w', 'location': '54'}, {'type': 'p', 'colour': 'w', 'location': '84'}, {'type': 'r', 'colour': 'w', 'location': '83'}, {'type': 'p', 'colour': 'w', 'location': '12'}, {'type': 'p', 'colour': 'w', 'location': '22'}, {'type': 'p', 'colour': 'w', 'location': '32'}, {'type': 'p', 'colour': 'w', 'location': '42'}, {'type': 'p', 'colour': 'w', 'location': '62'}, {'type': 'p', 'colour': 'w', 'location': '72'}, {'type': 'r', 'colour': 'w', 'location': '11'}, {'type': 'n', 'colour': 'w', 'location': '21'}, {'type': 'b', 'colour': 'w', 'location': '31'}, {'type': 'q', 'colour': 'w', 'location': '41'}, {'type': 'k', 'colour': 'w', 'location': '51'}, {'type': 'b', 'colour': 'w', 'location': '61'}, {'type': 'n', 'colour': 'w', 'location': '71'}]
        
        # set blank piece at the end to signify there is no more pieces left
        piece_list.append({
            "type": "",
            "colour": "",
            "location": ""
        })
        fen = ""
        blank_squares_counter = 0
        i = 0
        for rank in range(8, 0, -1):
            for file in range(1, 9):

                # check for castling rights
                if piece_list[i]["type"] == "k":
                    if piece_list[i]["colour"] == "w" and piece_list[i]["location"] != "51":
                        self._castling_rights = self._castling_rights.replace("KQ", "")
                    elif piece_list[i]["colour"] == "b" and piece_list[i]["location"] != "58":
                        self._castling_rights = self._castling_rights.replace("kq", "")
                
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

    def get_piece_list(self):
        # generate piece list
        pieces_DOM_elements = self._driver.find_elements(By.CSS_SELECTOR, ".board .piece")
        piece_list = []
        for piece in pieces_DOM_elements:
            class_names = piece.get_attribute("class").split(" ")
            if len(class_names) != 3: # if an incorrect element was found 
                return self.get_piece_list()
            
            for class_name in class_names:
                if len(class_name) == 2:
                    piece_type = class_name[1]
                    piece_colour = class_name[0]
                elif class_name.startswith("square-"):
                    location = class_name[-2::]
            
            piece_info = { 
                "type": piece_type,
                "colour": piece_colour,
                "location": location
            }
            piece_list.append(piece_info)

        piece_list.sort(key=lambda piece:int(piece["location"][0])) #sort left to right
        piece_list.sort(key=lambda piece:int(piece["location"][1]), reverse=True) #sort by rank
        return piece_list

    def wait_for_turn(self):
        loops = 0
        while True:  # keep looping until the game is over or it is my turn
            if loops % 5 == 0 and self.is_game_over():
                return False
            loops += 1
            if self.is_element_present(".board-layout-bottom .clock-player-turn"):
                # chime.success()
                return True

    def is_game_over(self):
        # try looking for the two class names
        return self.is_element_present(".live-game-buttons-game-over") or self.is_element_present(".game-result") or self.is_element_present(".game-over-modal-content")


    def start_new_game(self, auto_start_next_game=False):
        # game_over = True
        if auto_start_next_game:
            new_game_selector = ".live-game-buttons-game-over button"
            sleep(1.5)
            while not self._waiting_for_new_game: # press the new game button
                if self.is_element_present(new_game_selector):
                    print("game over buttons found")
                    self._waiting_for_new_game = True
                    new_game_buttons = self._driver.find_elements(By.CSS_SELECTOR, new_game_selector)
                    for game_button in new_game_buttons[::-1]: # press rematch button and find match button
                        try:
                            game_button.click()
                        except:
                            pass
                        sleep(2)

        while self.is_game_over(): # block until game is started
            sleep(0.1)
        self.wait_for_turn()
        self._game_started = True
        self._waiting_for_new_game = False
        board = self._driver.find_element(By.CSS_SELECTOR, ".board")
        self._player_colour = "b" if "flipped" in board.get_attribute("class") else "w"
        self._castling_rights = "KQkq"

    def block_while_my_turn(self):
        while True: # wait until my turn has finished properly (see opponents clock)
            sleep(0.05)
            if self.is_element_present(".board-layout-top .clock-player-turn"):
                return True
            else:
                if self.is_game_over():
                    return False


    def is_element_present(self, css_selector):
        try:
            self._driver.find_element(By.CSS_SELECTOR, css_selector)
            return True
        except:
            return False