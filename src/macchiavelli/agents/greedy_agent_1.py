from macchiavelli.game import Player 

class GreedyAgentV1(Player):
    """
    This agent considers every meld and if he can add a card to it then greedily adds it to the current meld.
    If he cannot add a card he will get back the unchanged table (this will result in him having to draw a card)
    """
    def get_move(self, table):
        cards_used = set()

        for i, meld in enumerate(table.table): 
            for card in self.cards: 
                if card in cards_used: 
                    continue 

                possible_meld = meld.append(card)
                if table.is_valid_meld(possible_meld): 
                    table.table[i] = possible_meld
                    cards_used.add(card)
                    break 

        return table 


