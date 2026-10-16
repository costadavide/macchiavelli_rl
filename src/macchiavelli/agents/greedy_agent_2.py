from macchiavelli.game import Player 

# goal: split pool into valid melds while using as many hand cards as possible
# use backtracking + memoization to make it faster 

class GreedyAgentV2(Player):
    def get_move(self, table):
        return super().get_move(table)