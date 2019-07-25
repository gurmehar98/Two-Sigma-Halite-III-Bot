import hlt
from hlt import constants
from hlt.positionals import Direction
import random
import logging

""" <<<Game Begin>>> """

game = hlt.Game()
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("MyPythonBot")
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

ship_states = {}
while True:
    game.update_frame()
    me = game.me
    game_map = game.game_map
    command_queue = []
    direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]
    position_choices = []
    for ship in me.get_ships():
        if ship.id not in ship_states:
            ship_states[ship.id] = "Collecting..."
        position_options = ship.position.get_surrounding_cardinals() + [ship.position]
        position_dict = {}
        halite_dict = {}
        for n, direction in enumerate(direction_order):
            position_dict[direction] = position_options[n]
        for direction in position_dict:
            position = position_dict[direction]
            halite_amount = game_map[position].halite_amount
            if position_dict[direction] not in position_choices:
                if direction == Direction.Still:
                    halite_dict[direction] = halite_amount * 2
                else:
                    halite_dict[direction] = halite_amount
        if ship_states[ship.id] == "Depositing...":
            move = game_map.naive_navigate(ship, me.shipyard.position)
            position_choices.append(position_dict[move])
            command_queue.append(ship.move(move))
            if move == Direction.Still:
                ship_states[ship.id] = "Collecting..." 
        elif ship_states[ship.id] == "Collecting...":
            directional_choice = max(halite_dict, key=halite_dict.get)
            position_choices.append(position_dict[directional_choice])
            command_queue.append(ship.move(game_map.naive_navigate(ship, position_dict[directional_choice])))
            if ship.halite_amount > constants.MAX_HALITE * 0.95:
                ship_states[ship.id] = "Depositing..."

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)