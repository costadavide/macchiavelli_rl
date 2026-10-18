from macchiavelli.game import Player 

class GreedyAgentV1(Player):
    """
    This agent considers every meld and if he can add a card to it then greedily adds it to the current meld.
    If he cannot add a card he return None (this will result in him having to draw a card)
    """
    def get_move(self, table):
        available_cards = self.cards.copy()

        for value in range(13):
            by_suit = {}
            for card in available_cards:
                if card.value == value:
                    by_suit[card.suit] = card

            if len(by_suit) >= 3:
                meld = list(by_suit.values())
                table.add_cards(meld)
                for card in meld:
                    available_cards.remove(card)

        for i, meld in enumerate(table.table): 
            for card in available_cards: 
                if card.suit != meld[0].suit and card.value != meld[0].value:
                    continue  

                possible_meld = meld + [card]
                if table.is_valid_meld(possible_meld): 
                    table.table[i] = possible_meld
                    available_cards.remove(card)
                    break 

        if len(available_cards) < len(self.cards):
            return table
        return None


