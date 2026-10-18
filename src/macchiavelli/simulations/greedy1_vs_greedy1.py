import random 
from collections import Counter
from macchiavelli.game import Macchiavelli
from macchiavelli.agents.greedy_agent_1 import GreedyAgentV1


def run(num_games=1000, seed=23):
    random.seed(seed)

    agent1 = GreedyAgentV1()
    agent2 = GreedyAgentV1()

    results = Counter()
    hand_left = {agent1: [], agent2: []}
    melds_on_table = []

    for game_num in range(num_games):
        order = [agent1, agent2] if game_num % 2 == 0 else [agent2, agent1]
        game = Macchiavelli(order)
        winner = game.play() 

        if winner is None: 
            results["draw"] += 1 
        elif winner is agent1:
            results["agent_1"] += 1
        else:
            results["agent_2"] += 1 

        hand_left[agent1].append(len(agent1.cards))
        hand_left[agent2].append(len(agent2.cards))
        melds_on_table.append(len(game.table.table))

    print(f"games: {num_games}")
    for key in ["agent_1", "agent_2", "draw"]:
        print(f"  {key}: {results[key]} ({results[key] / num_games:.1%})")

    for name, agent in [("agent_1", agent1), ("agent_2", agent2)]:
        sizes = hand_left[agent]
        print(f"{name} cards left in hand: avg {sum(sizes) / len(sizes):.1f}, min {min(sizes)}, max {max(sizes)}")

    print(f"avg melds on table at the end: {sum(melds_on_table) / num_games:.1f}")


def main():
    run()

if __name__ == "__main__":
    main()