from macchiavelli.game import Player, count_cards, Table, Card
from itertools import combinations
# goal: split pool into valid melds while using as many hand cards as possible
# use backtracking + memoization to make it faster 

def flatten(grid):
    n, m = len(grid), len(grid[0]) # 4, 13
    return tuple([grid[i][j] for i in range(n) for j in range(m)])

def melds_from_anchor(T, H, anchor):
    avail = [T[i]+H[i] for i in range(len(T))]
    s = anchor // 13 # suit of anchor 
    v = anchor % 13 # value of anchor
    melds = []

    other_suits = [t for t in range(4) if t!=s and avail[t*13+v] > 0]
    for k in (2, 3):
        for combo in combinations(other_suits, k): # combinations of other_suits with k elements
            melds.append([anchor] + [t*13+v for t in combo])

    run = [anchor]
    for w in range(v+1, 13):
        if avail[s*13+w] == 0:
            break 
        run.append(s*13+w)
        if len(run) >= 3:
            melds.append(list(run))

    if v == 0:
        run = [anchor]
        for w in range(12, 1, -1): # stop at 2 so don't get full run in both cases
            if avail[s*13+w] == 0:
                break 
            run.append(s*13+w)
            if len(run) >= 3:
                melds.append(list(run))

    return melds 

def consume(T, H, meld):
    gain = 0 # how many cards the meld used
    T_new = list(T)
    H_new = list(H)
    for card in meld:
        if T_new[card] > 0:
            T_new[card] -= 1 
        else: 
            H_new[card] -= 1
            gain += 1 

    return tuple(T_new), tuple(H_new), gain 

def solve(T, H, memo): 
    if (T, H) in memo:
        return memo[(T, H)][0]

    anchor = None 
    for i in range(52):
        if T[i] + H[i] > 0:
            anchor = i
            break 

    if anchor is None:
        memo[(T, H)] = (0, None, None) 
        return 0 
    best = -float("inf")
    best_meld = None 
    best_next = None 

    if H[anchor] > 0:# try to use card in our hand
        new_H = list(H)
        new_H[anchor] -= 1
        new_H = tuple(new_H)
        score = solve(T, new_H, memo)
        if score > best:
            best = score
            best_meld = None
            best_next = (T, new_H)

    for meld in melds_from_anchor(T, H, anchor):
        T2, H2, gain = consume(T, H, meld)
        score = gain+solve(T2, H2, memo)
        if score > best:
            best = score
            best_meld = meld  
            best_next = (T2, H2)
         
    memo[(T,H)] = (best, best_meld, best_next) 
    return best 

def get_melds(T, H, memo):
    melds = []
    state = (T, H)
    while state: 
        _, meld, state = memo[state]
        if meld:
            melds.append(meld)

    return melds 

    
class GreedyAgentV2(Player):
    def get_move(self, table):

        memo = {}
        T = flatten(table.table_counts)
        H = flatten(count_cards(self.cards))

        score = solve(T, H, memo)
        if score <=0:
            return None #draw a card 

        melds = get_melds(T, H, memo)
        new_table = Table()

        for meld in melds: 
            new_table.add_cards([Card(j%13, j// 13) for j in meld])

        return new_table
        
        



        

