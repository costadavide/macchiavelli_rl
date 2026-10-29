import random 
from collections import Counter
from macchiavelli.game import Macchiavelli
from macchiavelli.agents.greedy_agent_3 import GreedyAgentV3




def run(num_games=100, seed=23):
    random.seed(seed)

    agent1 = GreedyAgentV3()
    agent2 = GreedyAgentV3()
    agent3 = GreedyAgentV3()
    agent4 = GreedyAgentV3()

    results = Counter()
    hand_left = {agent1: [], agent2: [], agent3: [], agent4: []}
    melds_on_table = []

    for game_num in range(num_games):
        order = [agent1, agent2, agent3, agent4]
        random.shuffle(order)
        game = Macchiavelli(order)
        winner = game.play() 

        if winner is None: 
            results["draw"] += 1 
        elif winner is agent1:
            results["agent_1"] += 1
        elif winner is agent2:
            results["agent_2"] += 1 
        elif winner is agent3:
            results["agent_3"] += 1
        else: 
            results["agent_4"] += 1 

        hand_left[agent1].append(len(agent1.cards))
        hand_left[agent2].append(len(agent2.cards))
        hand_left[agent3].append(len(agent3.cards))
        hand_left[agent4].append(len(agent4.cards))
        melds_on_table.append(len(game.table.table))

        print(f"game {game_num} ended")

    print(f"games: {num_games}")
    for key in ["agent_1", "agent_2", "agent_3", "agent_4", "draw"]:
        print(f"  {key}: {results[key]} ({results[key] / num_games:.1%})")

    for name, agent in [("agent_1", agent1), ("agent_2", agent2), ("agent_3", agent3), ("agent_4", agent4)]:
        sizes = hand_left[agent]
        print(f"{name} cards left in hand: avg {sum(sizes) / len(sizes):.1f}, min {min(sizes)}, max {max(sizes)}")

    print(f"avg melds on table at the end: {sum(melds_on_table) / num_games:.1f}")


def main():
    run()

if __name__ == "__main__":
    main()