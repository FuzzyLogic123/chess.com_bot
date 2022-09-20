
from Client import Client
from Engine import Engine
from rich.console import Console

console = Console()

client = Client()
engine = Engine()

while True:
    client.wait_for_turn()
    console.print(client.get_time_remaining())
    next_move = engine.get_move(client.get_fen(), client.get_time_remaining())
    console.print(next_move, style="dark_orange3")
    input("press enter when you have moved")