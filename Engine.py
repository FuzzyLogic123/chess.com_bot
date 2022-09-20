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
            depth=8,
            parameters={
            "Slow Mover": 0,
            "Ponder": 'true',
            "Contempt": 100,
            })

    def get_move(self, fen, time_remaining):
        self._stockfish.set_fen_position(fen)
        if not self._stockfish.is_fen_valid(fen):
            return None

        self._stockfish.get_board_visual()
        
        best_move, play_instantly = self.get_best_move(time_remaining)
        delay = self.get_delay(time_remaining)
        play_instantly = True
        console.print(delay)
        if not play_instantly:
            time.sleep(delay)
        return best_move

    def get_best_move(self, time_remaining):
        NUMBER_OF_LINES = 5
        play_instantly = False
        t0 = time.time()
        if time_remaining < 5000:
            best_move = self._stockfish.get_best_move(wtime=time_remaining)
        else:
            best_moves = self._stockfish.get_top_moves(NUMBER_OF_LINES)
            # check that the move they make is not a straight up blunder

            random_number = random.randint(0, NUMBER_OF_LINES - 1)
            best_move = best_moves[min(random_number, len(best_moves)) - 1]["Move"]

            if best_moves[0]["Mate"] != None: # play mate if it exists
                best_move = best_moves[0]["Move"]
            elif abs(best_moves[0]["Centipawn"] - best_moves[-1]["Centipawn"]) > 100:
                best_move = best_moves[0]["Move"]
                play_instantly = True if self._stockfish.will_move_be_a_capture(best_move) == Stockfish.Capture.DIRECT_CAPTURE else False
        t1 = time.time()
        pprint(t1-t0)
        return best_move, play_instantly

    def get_delay(self, time_remaining):
        # if its a capture and every other move loses
        BULLET_GAME_TIME = 60000
        if self._move_counter < 10:
            time_factor = 1.5
        else:
            time_factor = 8
        realistic_delay = random.random() * time_factor * (time_remaining / BULLET_GAME_TIME)
        return realistic_delay