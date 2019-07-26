import hlt
from hlt import constants
from hlt.positionals import Direction, Position
import logging
import math

game = hlt.Game()
game.ready("MarkI")
ship_states = {}
while True:
    game.update_frame()
    me, game_map, command_queue, position_choices = game.me, game.game_map, [], []
    direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]
    for ship in me.get_ships():
        if ship.id not in ship_states: ship_states[ship.id] = "Collecting..."
        if ship_states[ship.id] == "Collecting...":
            position_options = ship.position.get_surrounding_cardinals() + [ship.position]
            position_dict, halite_dict = {}, {}
            for n, direction in enumerate(direction_order): position_dict[direction] = position_options[n]
            for direction in position_dict:
                position = position_dict[direction]
                halite_amount = game_map[position].halite_amount
                if position_dict[direction] not in position_choices:
                    if direction == Direction.Still: halite_amount *= 4
                    halite_dict[direction] = halite_amount
            directional_choice = max(halite_dict, key=halite_dict.get)
            position_choices.append(position_dict[directional_choice])
            command_queue.append(ship.move(game_map.naive_navigate(ship, ship.position+Position(*directional_choice))))
            if ship.halite_amount >= constants.MAX_HALITE * 0.95: ship_states[ship.id] = "Depositing..."
        elif ship_states[ship.id] == "Depositing...":
            move = game_map.naive_navigate(ship, me.shipyard.position)
            upcoming_position = ship.position + Position(*move)
            if upcoming_position not in position_choices:
                position_choices.append(upcoming_position)
                command_queue.append(ship.move(move))
                if move == Direction.Still: ship_states[ship.id] = "Collecting..."
            else:
                position_choices.append(ship.position)
                command_queue.append(ship.move(game_map.naive_navigate(ship, ship.position+Position(*Direction.Still))))
    if len(me.get_ships()) < math.ceil(game.turn_number / 25):
        if me.halite_amount >= 1000 and not game_map[me.shipyard].is_occupied: command_queue.append(me.shipyard.spawn())
    game.end_turn(command_queue)