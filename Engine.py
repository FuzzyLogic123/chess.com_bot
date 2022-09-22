import random
import time
from rich.pretty import pprint
from stockfish import Stockfish
from rich.console import Console

console = Console()

class Engine:
    def __init__(self):
        self._move_counter = 0
        self._stockfish = Stockfish(
            depth=10,
            parameters={
            "Slow Mover": 0,
            "Ponder": 'true',
            "Contempt": 100,
            "Skill Level": 1
            })

    def get_move(self, fen, time_remaining):
        self._stockfish.set_fen_position(fen)
        if not self._stockfish.is_fen_valid(fen):
            console.print(fen, style="red")
            return None
        # self._stockfish.get_board_visual()
        best_move, play_instantly = self.get_best_move(time_remaining)
        delay = self.get_delay(time_remaining)
        # print(delay)
        # play_instantly = True
        if not play_instantly:
            time.sleep(delay)
        self._move_counter += 1
        return best_move

    def get_best_move(self, time_remaining):
        play_instantly = False
        best_move = self._stockfish.get_best_move_time(50)
        play_instantly = self._stockfish.will_move_be_a_capture(best_move) == Stockfish.Capture.DIRECT_CAPTURE
        return best_move, play_instantly

    def get_delay(self, time_remaining):
        # if its a capture and every other move loses
        BULLET_GAME_TIME = 60000
        if self._move_counter < 5:
            time_factor = 1
        else:
            time_factor = 2.5
        realistic_delay = random.random() * time_factor * (time_remaining / BULLET_GAME_TIME)
        return realistic_delay