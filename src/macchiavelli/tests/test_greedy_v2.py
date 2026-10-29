from macchiavelli.agents.greedy_agent_2 import melds_from_anchor, consume, solve, get_melds
from macchiavelli.game import Card, Table
import random

def test_melds_from_anchor():
    random.seed(0) # same random tables every run, so a failure can be reproduced

    for _ in range(100):
        T = [random.randint(0, 1) for _ in range(52)]
        H = [random.randint(0, 1) for _ in range(52)]

        for i in range(52):
            anchor = i
            melds = melds_from_anchor(T, H, anchor)

            for meld in melds:
                # every meld contains the anchor
                assert anchor in meld
                # every other card in the meld is actually available
                assert all(T[j] + H[j] > 0 for j in meld if j != anchor)
                # no card used twice in the same meld
                assert len(set(meld)) == len(meld)
                # the meld follows the game rules
                cards = [Card(j % 13, j // 13) for j in meld]
                assert Table.is_valid_set(cards) or Table.is_valid_run(cards), f"invalid meld {cards} for anchor {anchor}"

            # no meld is generated twice
            assert len({tuple(sorted(meld)) for meld in melds}) == len(melds)

def test_consume():
    meld = [0, 1, 2] # A-2-3 of Hearts

    # all cards from the table: nothing gained
    T = tuple([1]*3 + [0]*49)
    H = tuple([0]*52)
    T_new, H_new, gain = consume(T, H, meld)
    assert gain == 0
    assert T_new == tuple([0]*52)
    assert H_new == H

    # all cards from the hand: every card counts
    T = tuple([0]*52)
    H = tuple([1]*3 + [0]*49)
    T_new, H_new, gain = consume(T, H, meld)
    assert gain == 3
    assert T_new == T
    assert H_new == tuple([0]*52)

    # same card on the table and in the hand: the table copy is used first
    T = tuple([1]*3 + [0]*49)
    H = tuple([1] + [0]*51)
    T_new, H_new, gain = consume(T, H, meld)
    assert gain == 0
    assert T_new == tuple([0]*52)
    assert H_new == H

    # two copies on the table (two decks): only one is used
    T = tuple([2] + [1]*2 + [0]*49)
    H = tuple([0]*52)
    T_new, H_new, gain = consume(T, H, meld)
    assert gain == 0
    assert T_new == tuple([1] + [0]*51)

    # mixed: one card from the table, two from the hand
    T = tuple([1] + [0]*51)
    H = tuple([0] + [1]*2 + [0]*49)
    T_new, H_new, gain = consume(T, H, meld)
    assert gain == 2
    assert T_new == tuple([0]*52)
    assert H_new == tuple([0]*52)

    # the inputs are not modified
    assert T == tuple([1] + [0]*51)
    assert H == tuple([0] + [1]*2 + [0]*49)



def counts(indices):
    # 52-tuple with one copy of each flat index (repeat an index for two copies)
    c = [0]*52
    for i in indices:
        c[i] += 1
    return tuple(c)

def test_solve():
    # flat index = suit*13 + value, ace = value 0 (Hearts 0, Diamonds 1, Clubs 2, Spades 3)

    # nothing to place
    assert solve(counts([]), counts([]), {}) == 0

    # empty table, hand 7♥ 7♣ 7♠ 2♦: the set is played, 2♦ is left out
    assert solve(counts([]), counts([6, 32, 45, 14]), {}) == 3

    # table 5-6-7♥, hand 8♥ 2♣: 8♥ goes on the run
    assert solve(counts([4, 5, 6]), counts([7, 27]), {}) == 1

    # table 2..8♥, hand 5♣ 5♠: the run has to be split into 2-3-4, 5-5-5, 6-7-8
    assert solve(counts(range(1, 8)), counts([30, 43]), {}) == 2

    # table A♥ 2♥ is not a valid meld and can't be fixed: impossible
    assert solve(counts([0, 1]), counts([]), {}) == float("-inf")

    # ace-high: table Q-K♥, hand A♥ makes Q-K-A
    assert solve(counts([11, 12]), counts([0]), {}) == 1

    # two decks: table has 7♥ twice and 7♣ 7♠ once, hand 7♣ 7♠ makes a second set
    assert solve(counts([6, 6, 32, 45]), counts([32, 45]), {}) == 2

    # only hand cards that fit are counted, even with a valid table
    assert solve(counts([0, 1, 2]), counts([3, 20, 50]), {}) == 1


def check_melds(T, H):
    # solve, then check that the melds from get_melds are a legal way to reach the score
    memo = {}
    score = solve(T, H, memo)
    melds = get_melds(T, H, memo)

    for meld in melds:
        cards = [Card(j % 13, j // 13) for j in meld]
        assert Table.is_valid_set(cards) or Table.is_valid_run(cards), f"invalid meld {cards}"

    used = counts([j for meld in melds for j in meld])
    for i in range(52):
        # every table card is placed, and no card is used more times than it exists
        assert T[i] <= used[i] <= T[i] + H[i]

    # the hand cards placed are exactly the score
    assert sum(used) - sum(T) == score
    return score

def test_get_melds():
    # same positions as test_solve
    assert check_melds(counts([]), counts([])) == 0
    assert check_melds(counts([]), counts([6, 32, 45, 14])) == 3
    assert check_melds(counts([4, 5, 6]), counts([7, 27])) == 1
    assert check_melds(counts(range(1, 8)), counts([30, 43])) == 2
    assert check_melds(counts([11, 12]), counts([0])) == 1
    assert check_melds(counts([6, 6, 32, 45]), counts([32, 45])) == 2
    assert check_melds(counts([0, 1, 2]), counts([3, 20, 50])) == 1

    # random hands on an empty table, drawn from two decks
    random.seed(0)
    two_decks = list(range(52)) * 2
    for _ in range(200):
        check_melds(counts([]), counts(random.sample(two_decks, 13)))


if __name__ == "__main__":
    test_melds_from_anchor()
    test_consume()
    test_solve()
    test_get_melds()
    print("all tests passed")
