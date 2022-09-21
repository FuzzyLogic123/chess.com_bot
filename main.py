
from Client import Client
from Engine import Engine
from rich.console import Console
from rich.traceback import install

install(show_locals=True)
console = Console()

class Main:
    def __init__(self):
        self._client = Client()
        self._engine = Engine()
        self.make_moves()

    def make_moves(self):
        while True:
            if not self._client.wait_for_turn():
                console.print("Game Over", style="salmon1")
                self._client.start_new_game()
            else:
                next_move = self.get_next_move()
                self._client.move(next_move)
                console.print(next_move, style="dark_orange3")

    def get_next_move(self):
        next_move = self._engine.get_move(self._client.get_fen(), self._client.get_time_remaining())
        if next_move == None:
            return self.get_next_move()
        else:
            return next_move

main = Main()