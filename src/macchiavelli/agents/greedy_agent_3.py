from macchiavelli.game import Player, count_cards, Table, Card
from itertools import product
# goal: split table + hand into valid melds, using every table card and as many hand cards as possible
# same goal as V2, but instead of backtracking card by card we do a dynamic programming over the values
# A, 2, ..., K, A (the ace comes back at the end for Q-K-A runs).
# at each value we only need to remember, for each suit:
#   - the lengths of the runs still open (1, 2 or 3 = "3 or more"), at most 2 since there are 2 decks
#     4 = "3 or more, started from the low ace": it can't take the high ace too (no A-...-K-A)
#   - how many aces were used low, so the high ace doesn't reuse the same copies
# so the number of states doesn't grow with the size of the table

NUM_POS = 14 # positions 0..12 are the values A..K, position 13 is the ace again (high)

def flatten(grid):
    n, m = len(grid), len(grid[0]) # 4, 13
    return tuple([grid[i][j] for i in range(n) for j in range(m)])

def set_groups(k):
    # k[s] = copies of suit s that go into sets at this value
    # returns the sets as lists of suits, or None if k can't be split into sets of 3-4 different suits
    most = max(k)
    if most == 0:
        return []
    if most == 1:
        group = [s for s in range(4) if k[s]]
        return [group] if len(group) >= 3 else None
    # a suit with 2 copies must be in two different sets, so we need exactly two sets of 3-4 cards
    if not 6 <= sum(k) <= 8:
        return None
    a = [s for s in range(4) if k[s] == 2]
    b = list(a)
    for s in range(4):
        if k[s] == 1:
            (a if len(a) <= len(b) else b).append(s)
    return [a, b]

# every way of putting 0-2 copies per suit into sets, with the sets it makes
SET_SPLITS = {k: g for k in product(range(3), repeat=4) if (g := set_groups(k)) is not None}
NO_SETS = (0, 0, 0, 0)

def grow(l, p):
    # length of an open run after adding the card at position p
    # a run with 3 cards at position 2 can only have started from the low ace
    if l == 4 or (l == 2 and p == 2):
        return 4
    return min(l+1, 3)

def extend_runs(runs, r, p):
    # runs: sorted tuple of open run lengths in one suit, r: copies of the current card that go into runs
    # the r shortest runs are extended (a short run left behind would be invalid), extra copies start new runs
    # a run from the low ace can also be closed and the card start a new run instead, so that run can take the high ace
    # returns [(new sorted tuple, how many low ace runs were closed instead of extended)], empty if nothing is valid
    if any(l < 3 for l in runs[r:]):
        return []
    extended = runs[:r]
    options = []
    for j in range(extended.count(4) + 1):
        kept = extended[:len(extended)-j] # sorted, so the low ace runs are the last ones
        if p == 13 and 4 in kept:
            continue
        new = [grow(l, p) for l in kept] + [1]*(r - len(kept))
        options.append((tuple(sorted(new)), j))
    return options

def suit_options(runs, lo, hi, p):
    # all the ways to place between lo and hi copies of one card at position p (no sets with the high ace)
    # returns {copies in sets: [(copies placed, new open runs, low ace runs closed)]}
    options = {}
    for c in range(lo, hi+1):
        for k in range(c+1 if p < 13 else 1):
            for new_runs, j in extend_runs(runs, c-k, p):
                options.setdefault(k, []).append((c, new_runs, j))
    return options

def card_range(T, H, i, p, low):
    # how many copies of card i can be placed at position p
    if p == 0:
        return 0, T[i]+H[i] # table aces can still be placed high
    if p == 13:
        return max(0, T[i]-low), T[i]+H[i]-low # table aces not used low must be used here
    return T[i], T[i]+H[i]

def solve(T, H):
    """
    Returns (score, melds): the most hand cards that can be placed and melds that do it,
    or (-inf, None) if the table cards can't be split into valid melds.
    """
    # state = (open runs per suit, aces used low per suit), layer maps state -> cards placed so far
    start = (((), (), (), ()), NO_SETS)
    layer = {start: 0}
    history = [] # history[p][state] = (previous state, copies placed per suit, copies in sets per suit)

    for p in range(NUM_POS):
        v = p % 13
        new_layer = {}
        back = {}
        for state, placed in layer.items():
            runs, low = state
            options = [suit_options(runs[s], *card_range(T, H, s*13+v, p, low[s]), p) for s in range(4)]

            for ks in (SET_SPLITS if p < 13 else [NO_SETS]):
                if not all(ks[s] in options[s] for s in range(4)):
                    continue
                for combo in product(*(options[s][ks[s]] for s in range(4))):
                    cs = tuple(c for c, _, _ in combo)
                    js = tuple(j for _, _, j in combo)
                    new_state = (tuple(r for _, r, _ in combo), cs if p == 0 else low)
                    score = placed + sum(cs)
                    if score > new_layer.get(new_state, -1):
                        new_layer[new_state] = score
                        back[new_state] = (state, cs, ks, js)

        history.append(back)
        layer = new_layer

    # every run still open at the end must have at least 3 cards
    best_state = None
    best = -1
    for state, placed in layer.items():
        if all(l >= 3 for runs in state[0] for l in runs) and placed > best:
            best, best_state = placed, state
    if best_state is None:
        return -float("inf"), None

    return best - sum(T), build_melds(history, best_state)

def build_melds(history, state):
    # walk the back pointers to get the decisions, then replay them with the actual cards
    decisions = []
    for p in range(NUM_POS-1, -1, -1):
        state, cs, ks, js = history[p][state]
        decisions.append((cs, ks, js))
    decisions.reverse()

    melds = []
    open_runs = [[] for _ in range(4)]
    for p, (cs, ks, js) in enumerate(decisions):
        v = p % 13
        for group in SET_SPLITS[ks]:
            melds.append([s*13+v for s in group])
        for s in range(4):
            r = cs[s] - ks[s]
            # same shortest-first rule as extend_runs: a run from the low ace is always the longest, so it's last
            runs = sorted(open_runs[s], key=len)
            kept = runs[:min(r, len(runs)) - js[s]]
            melds.extend(runs[len(kept):]) # runs not extended are closed
            for run in kept:
                run.append(s*13+v)
            open_runs[s] = kept + [[s*13+v] for _ in range(r - len(kept))]

    for runs in open_runs:
        melds.extend(runs)
    return melds


class GreedyAgentV3(Player):
    def get_move(self, table):
        T = flatten(table.table_counts)
        H = flatten(count_cards(self.cards))

        score, melds = solve(T, H)
        if score <= 0:
            return None #draw a card

        new_table = Table()
        for meld in melds:
            new_table.add_cards([Card(j%13, j//13) for j in meld])

        return new_table
