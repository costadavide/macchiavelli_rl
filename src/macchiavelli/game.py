import random
from enum import IntEnum


class MoveResult(IntEnum):
    INVALID = 0
    VALID = 1
    NO_CHANGE = -1 # table didn't change, so the player should draw a card


def count_cards(cards):
    # 4x13 grid with how many copies of each (suit, value) appear in cards
    counts = [[0]*13 for _ in range(4)]
    for card in cards:
        counts[card.suit][card.value] += 1
    return counts

class Deck: 
    def __init__(self, deck_num=0):
        self.cards = []
        self.size = 52
        self.deck_num = deck_num
        self.create()

    def create(self):
        suits = [0, 1, 2, 3] # {0: "Hearts", 1: "Diamonds", 2: "Clubs", 3: "Spades"}

        for suit in suits: 
            for value in range(0, (self.size // 4)): # values 0-12 for each suit  
                self.cards.append(Card(value, suit, deck_num=self.deck_num))

    def shuffle(self): 
        random.shuffle(self.cards)

    def draw(self): 
        if len(self.cards) == 0:
            raise ValueError("No cards left in the deck")
        return self.cards.pop()


class Card:
    # Cards are never modified after creation, so they can be shared between tables instead of copied
    suit_names = {0: "Hearts", 1: "Diamonds", 2: "Clubs", 3: "Spades"}

    def __init__(self, value, suit, deck_num=None):
        self.value = value
        self.suit = suit
        self.deck_num = deck_num

    def __repr__(self):
        return f"{self.value+1} of {self.suit_names[self.suit]}"

    def __str__(self):
        return f"{self.value+1} of {self.suit_names[self.suit]}"

    # deck_num is ignored: the same card from the two decks is interchangeable in play
    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return (self.value, self.suit) == (other.value, other.suit)

    def __hash__(self):
        return hash((self.value, self.suit))


class Macchiavelli: 
    def __init__(self, players): 
        if (not isinstance(players, list)) or (not all(isinstance(player, Player) for player in players)):
            raise ValueError("Players must be a list of Player objects")
        
        num_players = len(players)

        if num_players < 2 or num_players > 6:
            raise ValueError("Number of players must be between 2 and 6")
        
        self.deck1 = Deck(deck_num=0)
        self.deck2 = Deck(deck_num=1)
        self.num_players = num_players 
        self.starting_cards = {2: 13, 3: 9, 4: 7}.get(num_players, 5)
        self.players = players
        self.table = Table() # Look at Table class below to understand how this works
        self.curr_player_index = 0
        self.consecutive_passes = 0 # turns in a row where a player couldn't play nor draw
        self.game_over = False
        self.winner = None # stays None if the game ends in a draw

    def cards_left(self):
        return len(self.deck1.cards) + len(self.deck2.cards)

    def start_game(self):
        self.deck1.shuffle()
        self.deck2.shuffle()

        # players may be reused across games, so start from an empty hand
        for player in self.players:
            player.cards = []
            player.your_turn = False

        for player in self.players:
            self.deal_cards(self.starting_cards, player)
        
        # consider whether to implement a randomization of the first player to start (but this could be done in the simulation logic)
        self.players[self.curr_player_index].your_turn = True

    def deal_cards(self, num_cards, player):
        #to be used in start_game to deal cards to each player + whenever a player has to "fish"
        cards_drawn = []
        for i in range(num_cards): 
            if self.deck1.cards and self.deck2.cards:
                # draw from either deck
                prob = random.random()
                if prob < 0.5: 
                    cards_drawn.append(self.deck1.draw())
                else: 
                    # draw from deck2
                    cards_drawn.append(self.deck2.draw())
            elif self.deck1.cards:
                cards_drawn.append(self.deck1.draw())
            elif self.deck2.cards:
                cards_drawn.append(self.deck2.draw())
            else: 
                raise ValueError("No cards left to draw")

        player.cards.extend(cards_drawn)


    def player_turn(self, player):
        """
        Logic for a player's turn: ask for a player's move (a Table object), validate it and if valid apply it.
        An invalid move is treated like no move: the player draws a card, or passes if the decks are empty.
        Ends the game when the player empties their hand (win) or when every player passed in a row with empty decks (draw).

        Returns: the MoveResult of the player's move, so a training loop can turn it into a reward.
        """
        if self.game_over:
            raise ValueError("The game is over")
        if not player.your_turn:
            raise ValueError("It's not this player's turn")

        # pass a copy so the player can't modify the real table in place
        player_move = player.get_move(self.table.copy())

        if player_move is None:
            result = MoveResult.NO_CHANGE
        else:
            result = self.table.validate_move(player_move, player)

        if result == MoveResult.VALID:
            cards_added = self.table.cards_added(player_move)
            self.table.apply_move(player_move)
            # remove the cards from the player's hand
            for card in cards_added:
                player.cards.remove(card)
            self.consecutive_passes = 0

            if not player.cards:
                self.game_over = True
                self.winner = player
        elif self.cards_left() > 0:
            # NO_CHANGE or INVALID: draw a card
            self.deal_cards(1, player)
            self.consecutive_passes = 0
        else:
            # nothing to draw: pass the turn
            self.consecutive_passes += 1
            if self.consecutive_passes >= self.num_players:
                self.game_over = True # draw, self.winner stays None

        player.your_turn = False
        # Move to the next player
        self.curr_player_index = (self.curr_player_index + 1) % self.num_players
        self.players[self.curr_player_index].your_turn = True

        return result

    def play(self):
        """
        Play a full game from the start.
        Returns: the winning Player, or None if the game ended in a draw.
        """
        self.start_game()
        while not self.game_over:
            self.player_turn(self.players[self.curr_player_index])
        return self.winner


class Player: 
    def __init__(self):
        self.cards = []
        self.your_turn = False 

    def get_move(self, table):
        """
        This method should be implemented to get the player's move. 
        If want to fish a card, return None
        Returns: a Table object representing the new state of the table after the player's move.
        """ 
        return None


class Table: 
    def __init__(self):
        self.table = [] 
        self.table_counts = [[0]*13 for _ in range(4)] # 4 suits, 13 values

    def copy(self):
        # new meld lists, same (immutable) Card objects: much faster than copy.deepcopy
        new = Table()
        new.table = [list(meld) for meld in self.table]
        new.table_counts = [list(row) for row in self.table_counts]
        return new

    def add_cards(self, cards):
        # cards is a list of Card objects 
        assert isinstance(cards, list), "cards should be a list of Card objects"
        for card in cards:
            assert isinstance(card, Card), "each item in cards should be a Card object"
        
        for card in cards:
            self.table_counts[card.suit][card.value] += 1

        self.table.append(list(cards)) # own copy, so later changes to the caller's list don't leak into the table

    @staticmethod
    def is_valid_set(meld):
        # 3-4 cards with the same value and all different suits
        if not 3 <= len(meld) <= 4:
            return False
        if len({card.value for card in meld}) != 1:
            return False
        return len({card.suit for card in meld}) == len(meld)

    @staticmethod
    def is_valid_run(meld):
        # 3+ consecutive cards of the same suit. Ace (value 0) can be low (A-2-3) or high (Q-K-A), no wrap-around
        if len(meld) < 3:
            return False
        if len({card.suit for card in meld}) != 1:
            return False

        values = sorted(card.value for card in meld)
        if values == list(range(values[0], values[0] + len(values))):
            return True

        # try the ace as high (value 13)
        if values[0] == 0:
            values = sorted(values[1:] + [13])
            return values == list(range(values[0], values[0] + len(values)))
        return False

    def is_valid_meld(self, meld):
        return self.is_valid_set(meld) or self.is_valid_run(meld)

    def cards_added(self, move):
        """
        Cards on move's table that are not on the current table, or None if move removes any card from the table.
        Counts are recomputed from move.table so an inconsistent move.table_counts can't be used to cheat.
        """
        new_counts = count_cards(card for meld in move.table for card in meld)
        added = []
        for suit in range(4):
            for value in range(13):
                diff = new_counts[suit][value] - self.table_counts[suit][value]
                if diff < 0:
                    return None
                added.extend([Card(value, suit)] * diff)
        return added

    def validate_move(self, move, player):
        """
        Stuff to check:
        1. That the cards added to the table are in the player's hand (final table - starting table)
        2. That the new table follows all the game rules 

        returns a MoveResult:
        - INVALID if the table proposed is not valid
        - VALID if the table proposed is valid 
        - NO_CHANGE if the table didn't change, so actually you should draw a card
        """
        if not isinstance(move, Table):
            return MoveResult.INVALID

        # get cards added by player, compared to starting table 
        cards_added = self.cards_added(move)
        if cards_added is None:
            return MoveResult.INVALID
        if not cards_added:
            return MoveResult.NO_CHANGE

        # the player must hold enough copies of every card added
        hand_counts = count_cards(player.cards)
        added_counts = count_cards(cards_added)
        for suit in range(4):
            for value in range(13):
                if added_counts[suit][value] > hand_counts[suit][value]:
                    return MoveResult.INVALID

        if not all(self.is_valid_meld(meld) for meld in move.table):
            return MoveResult.INVALID

        return MoveResult.VALID

    def apply_move(self, move):
        # replace the table with the (already validated) proposed one
        self.table = [list(meld) for meld in move.table]
        self.table_counts = count_cards(card for meld in self.table for card in meld)
