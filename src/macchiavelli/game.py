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
        self.starting_cards = {2: 13, 3: 9, 4: 7}.get(num_players, 5)
        self.players = [Player() for _ in range(num_players)]
        self.table = None # Decide how to define this. It should hold cards that are on the table

    def start_game(self): 
        self.deck1.shuffle()
        self.deck2.shuffle()

        for player in self.players:
            self.deal_cards(self.starting_cards, player)
        
        self.players[0].your_turn = True

    def deal_cards(self, num_cards, player):
        #to be used in start_game to deal cards to each player + whenever a player has to "fish"
        cards_drawn = []
        for i in range(num_cards): 
            prob = random.random()
            if prob < 0.5 and self.deck1.cards: 
                # draw from deck1
                cards_drawn.append(self.deck1.draw())
            else: 
                # draw from deck2
                cards_drawn.append(self.deck2.draw())

        player.cards.extend(cards_drawn)


    def player_turn(self, player):
        # logic for a player's turn
        # ask for a player's move (a Move object), then validate it and if valid apply it and move to next player. Else ask again for a move
        pass 

class Player: 
    def __init__(self):
        self.cards = []
        self.your_turn = False 

class Move: 
    def __init__(self): 
        pass 

    def propose(self):
        pass

    def validate(self):
        pass


