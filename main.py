
from Client import Client
from Engine import Engine
from rich.console import Console
from rich.traceback import install

install(show_locals=True)
console = Console()

client = Client()
engine = Engine()

while True:
    client.wait_for_turn()
    console.print(client.get_time_remaining())
    next_move = engine.get_move(client.get_fen(), client.get_time_remaining())
    if not next_move:
        console.print("Game over", style="salmon1")
        client = Client() # this will reload the chess.com home page, instead create a start game method, and make this called in init and when game over
    console.print(next_move, style="dark_orange3")
    input("press enter when you have moved")