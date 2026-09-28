import random

class Deck: 
    def __init__(self, deck_num=0):
        self.cards = []
        self.size = 52
        self.create()
        self.deck_num = deck_num

    def create(self):
        suits = [0, 1, 2, 3] # {0: "Hearts", 1: "Diamonds", 2: "Clubs", 3: "Spades"}

        for suit in suits: 
            for value in range(1, (self.size // 4) + 1): 
                self.cards.append(Card(value, suit, deck_num=self.deck_num))

    def shuffle(self): 
        random.shuffle(self.cards)

    def draw(self): 
        if len(self.cards) == 0:
            raise ValueError("No cards left in the deck")
        return self.cards.pop()


class Card:
    def __init__(self, value, suit, deck_num=None):
        self.value = value
        self.suit = suit
        self.deck_num = deck_num
        self.suit_names = {0: "Hearts", 1: "Diamonds", 2: "Clubs", 3: "Spades"}

    def __repr__(self):
        return f"{self.value} of {self.suit_names[self.suit]}"

    def __str__(self):
        return f"{self.value} of {self.suit_names[self.suit]}"


class Macchiavelli: 
    def __init__(self, players): 
        num_players = len(players)
        if (not isinstance(players, list)) or (not all(isinstance(player, Player) for player in players)):
            raise ValueError("Players must be a list of Player objects")
        if num_players < 2 or num_players > 6:
            raise ValueError("Number of players must be between 2 and 6")
        
        self.deck1 = Deck(deck_num=0)
        self.deck2 = Deck(deck_num=1)
        self.num_players = num_players 
        self.starting_cards = {2: 13, 3: 9, 4: 7}.get(num_players, 5)
        self.players = players
        self.table = Table() # Look at Table class below to understand how this works
        self.curr_player_index = 0

    def start_game(self): 
        self.deck1.shuffle()
        self.deck2.shuffle()

        for player in self.players:
            self.deal_cards(self.starting_cards, player)
        
        # consider whether to implement a randomization of the first player to start (but this could be done in the simulation logic)
        self.players[self.curr_player_index].your_turn = True

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
        if not player.your_turn:
            raise ValueError("It's not this player's turn")

        player_move, cards_added = player.get_move(self.table) 

        if player_move is None:
            self.deal_cards(1, player)
        elif self.table.validate_move(player_move):
            self.table.add_cards(cards_added)
            # remove the cards from the player's hand
            for card in cards_added:
                player.cards.remove(card)
        else: 
            raise ValueError("Invalid move")


        player.your_turn = False
        # Move to the next player 
        self.curr_player_index = (self.curr_player_index + 1) % self.num_players
        self.players[self.curr_player_index].your_turn = True
        

class Player: 
    def __init__(self):
        self.cards = []
        self.your_turn = False 

    def get_move(self, table):
        """
        This method should be implemented to get the player's move. 
        If want to fish a card, return None
        Returns: a Move object representing the new state of the table after the player's move, a list with the cards added to the table.
        """ 
        pass 


class Table: 
    def __init__(self):
        self.table = [] 
        self.table_counts = [[0]*13 for _ in range(4)] # 4 suits, 13 values

    def add_cards(self, cards):
        # cards is a list of Card objects 
        assert isinstance(cards, list), "cards should be a list of Card objects"
        for card in cards:
            assert isinstance(card, Card), "each item in cards should be a Card object"
        
        for card in cards:
            self.table_counts[card.suit][card.value] += 1

        self.table.extend(cards)

    def validate_move(self, move):
        """
        Stuff to check:
        1. That the cards added to the table are in the player's hand (final table - starting table)
        2. That the new table follows all the game rules 
        """
        pass