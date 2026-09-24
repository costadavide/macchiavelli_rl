import random

class Deck: 
    def __init__(self):
        self.cards = []
        self.size = 52
        self.create()

    def create(self):
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]

        for suit in suits: 
            for value in range(1, (self.size // 4) + 1): 
                self.cards.append(Card(value, suit))

    def shuffle(self): 
        random.shuffle(self.cards)

    def draw(self): 
        if len(self.cards) == 0:
            raise ValueError("No cards left in the deck")
        return self.cards.pop()


class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __repr__(self):
        return f"{self.value} of {self.suit}"

    def __str__(self):
        return f"{self.value} of {self.suit}"


class Macchiavelli: 
    def __init__(self, num_players): 
        self.deck1 = Deck()
        self.deck2 = Deck()
        self.num_players = num_players

    def start_game(self): 
        self.deck1.shuffle()
        self.deck2.shuffle()
        # shuffle the two decks (and combine them together)
        # assign cards to players, how many depends on how many players there are
        # determine the order of play
        pass 

    def deal_cards(self, num_cards, player):
        #to be used in start_game to deal cards to each player + whenever a player has to "fish"
        for i in range(...): 
            prob = random.random()
            if prob < 0.5: 
                # draw from deck1
                pass
            else: 
                # draw from deck2
                pass



class Player: 
    def __init__(self):
        self.cards = []
        self.your_turn = False 


