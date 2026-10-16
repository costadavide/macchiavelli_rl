from macchiavelli.game import Player
import random

class RandomAgent(Player):
    def get_move(self, table):
        if random.random() < 0.5 or not table.table or not self.cards: 
            return None # draw 
        else: 
            # get one card at random and add it to a random meld
            n = len(self.cards)
            card = random.choice(self.cards)
            m = len(table.table)
            table.table[random.randint(0, m-1)].append(card)

        return table 