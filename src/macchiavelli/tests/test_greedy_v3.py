from macchiavelli.agents.greedy_agent_3 import set_groups, extend_runs, solve
from macchiavelli.agents import greedy_agent_2
from macchiavelli.game import Card, Table
import random

def counts(indices):
    # 52-tuple with one copy of each flat index (repeat an index for two copies)
    c = [0]*52
    for i in indices:
        c[i] += 1
    return tuple(c)

def test_set_groups():
    # no sets
    assert set_groups((0, 0, 0, 0)) == []
    # one set of 3 or 4 suits
    assert set_groups((1, 1, 1, 0)) == [[0, 1, 2]]
    assert set_groups((1, 1, 1, 1)) == [[0, 1, 2, 3]]
    # less than 3 cards can't make a set
    assert set_groups((1, 1, 0, 0)) is None
    # two copies of a suit need two sets, so at least 6 cards
    assert set_groups((2, 1, 1, 1)) is None
    assert set_groups((2, 2, 0, 0)) is None

    # every split that is accepted makes sets of 3-4 different suits using exactly the copies in k
    for k in [(2, 2, 2, 0), (2, 2, 1, 1), (2, 2, 2, 1), (2, 2, 2, 2), (1, 0, 1, 1)]:
        groups = set_groups(k)
        assert groups is not None
        for group in groups:
            assert 3 <= len(group) <= 4
            assert len(set(group)) == len(group)
        assert [sum(group.count(s) for group in groups) for s in range(4)] == list(k)

def test_extend_runs():
    # lengths: 1, 2, 3 = "3 or more", 4 = "3 or more, started from the low ace"

    # new runs from nothing
    assert extend_runs((), 2, 5) == [((1, 1), 0)]
    # the shortest run is extended, the long one is closed
    assert extend_runs((1, 3), 1, 5) == [((2,), 0)]
    # a short run that is not extended can't be closed
    assert extend_runs((1, 2), 1, 5) == []
    assert extend_runs((2,), 0, 5) == []
    # a run with 3 cards at position 2 started from the low ace
    assert extend_runs((2,), 1, 2) == [((4,), 0)]
    # a run from the low ace can be extended, or closed and the card starts a new run
    assert extend_runs((4,), 1, 7) == [((4,), 0), ((1,), 1)]
    # but it can't take the high ace
    assert extend_runs((4,), 1, 13) == [((1,), 1)]
    assert extend_runs((3,), 1, 13) == [((3,), 0)]


def test_solve():
    # flat index = suit*13 + value, ace = value 0 (Hearts 0, Diamonds 1, Clubs 2, Spades 3)
    # same positions as test_greedy_v2

    # nothing to place
    assert solve(counts([]), counts([]))[0] == 0

    # empty table, hand 7♥ 7♣ 7♠ 2♦: the set is played, 2♦ is left out
    assert solve(counts([]), counts([6, 32, 45, 14]))[0] == 3

    # table 5-6-7♥, hand 8♥ 2♣: 8♥ goes on the run
    assert solve(counts([4, 5, 6]), counts([7, 27]))[0] == 1

    # table 2..8♥, hand 5♣ 5♠: the run has to be split into 2-3-4, 5-5-5, 6-7-8
    assert solve(counts(range(1, 8)), counts([30, 43]))[0] == 2

    # table A♥ 2♥ is not a valid meld and can't be fixed: impossible
    assert solve(counts([0, 1]), counts([])) == (float("-inf"), None)

    # ace-high: table Q-K♥, hand A♥ makes Q-K-A
    assert solve(counts([11, 12]), counts([0]))[0] == 1

    # two decks: table has 7♥ twice and 7♣ 7♠ once, hand 7♣ 7♠ makes a second set
    assert solve(counts([6, 6, 32, 45]), counts([32, 45]))[0] == 2

    # only hand cards that fit are counted, even with a valid table
    assert solve(counts([0, 1, 2]), counts([3, 20, 50]))[0] == 1

def test_solve_aces():
    # the ace can be low or high in a run, but not at both ends (no A-...-K-A)
    assert not Table.is_valid_run([Card(v, 0) for v in range(13)] + [Card(0, 0)])

    # hand A..K♥ and another A♥: A-...-J and Q-K-A
    assert check_melds(counts([]), counts(list(range(13)) + [0])) == 14

    # table A..K♥, hand A♥: the run is split so the second ace goes high
    assert check_melds(counts(range(13)), counts([0])) == 1

    # same with two decks
    assert check_melds(counts(list(range(13))*2), counts([0, 0])) == 2

    # A-2-3♥ and Q-K-A♥ use both copies of A♥
    assert check_melds(counts([]), counts([0, 1, 2, 11, 12, 0])) == 6

    # only one A♥: it can be low or high but not both
    assert check_melds(counts([]), counts([0, 1, 2, 11, 12])) == 3


def check_melds(T, H):
    # solve, then check that the melds are a legal way to reach the score
    score, melds = solve(T, H)

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

def test_melds():
    # same positions as test_solve
    assert check_melds(counts([]), counts([])) == 0
    assert check_melds(counts([]), counts([6, 32, 45, 14])) == 3
    assert check_melds(counts([4, 5, 6]), counts([7, 27])) == 1
    assert check_melds(counts(range(1, 8)), counts([30, 43])) == 2
    assert check_melds(counts([11, 12]), counts([0])) == 1
    assert check_melds(counts([6, 6, 32, 45]), counts([32, 45])) == 2
    assert check_melds(counts([0, 1, 2]), counts([3, 20, 50])) == 1

def test_same_score_as_v2():
    # V2 is exact but slow, so compare on small random positions
    random.seed(0)
    two_decks = list(range(52)) * 2

    for _ in range(300):
        # empty table
        hand = random.sample(two_decks, random.randint(0, 16))
        T, H = counts([]), counts(hand)
        assert check_melds(T, H) == greedy_agent_2.solve(T, H, {})

        # valid table made from the melds of that hand, plus new hand cards
        _, melds = solve(T, H)
        T = counts([j for meld in melds for j in meld])
        rest = list(two_decks)
        for j in range(52):
            for _ in range(T[j]):
                rest.remove(j)
        H = counts(random.sample(rest, random.randint(0, 8)))
        assert check_melds(T, H) == greedy_agent_2.solve(T, H, {})

    # random tables, mostly impossible
    for _ in range(100):
        T = counts(random.sample(two_decks, random.randint(1, 10)))
        H = counts(random.sample(two_decks, 4))
        assert solve(T, H)[0] == greedy_agent_2.solve(T, H, {})


if __name__ == "__main__":
    test_set_groups()
    test_extend_runs()
    test_solve()
    test_solve_aces()
    test_melds()
    test_same_score_as_v2()
    print("all tests passed")
