from game import Macchiavelli, Player

player1 = Player()
player2 = Player()
match = Macchiavelli(players=[player1, player2])

match.start_game()


while True: 
    current_player = match.players[match.curr_player_index]
    print(f"Player {match.curr_player_index + 1}'s turn")
    print(f"Current hand: {current_player.cards}")
    print(f"Current table: {match.table}")

    try:
        match.player_turn(current_player)
    except ValueError as e:
        print(e)
        continue