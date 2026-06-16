import json
import itertools
from multiprocessing import Pool
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_engine.game import SneakPeekGame
from bot.parameterized_bot import ParameterizedBot

def play_match(args):
    """
    Worker function for multiprocessing. 
    Plays a match between two bots and returns the bankroll delta.
    """
    name1, params1, name2, params2, num_rounds = args
    
    p1 = ParameterizedBot(name=name1, params=params1)
    p2 = ParameterizedBot(name=name2, params=params2)
    
    # Setting rounds. Real run is 10000.
    game = SneakPeekGame(p1, p2, rounds=num_rounds, starting_chips=5000, sb=10, bb=20)
    game.run()
    
    return name1, p1.bankroll, name2, p2.bankroll

class TournamentManager:
    def __init__(self, population_file, match_rounds=10000):
        with open(population_file, 'r') as f:
            self.population = json.load(f)
        self.match_rounds = match_rounds
        self.leaderboard = {name: 0.0 for name in self.population.keys()}
        
    def run_tournament(self, threads=4):
        bot_names = list(self.population.keys())
        matchups = list(itertools.combinations(bot_names, 2))
        
        # Prepare args
        tasks = []
        for n1, n2 in matchups:
            tasks.append((n1, self.population[n1], n2, self.population[n2], self.match_rounds))
            
        print(f"Starting {len(matchups)} matches of {self.match_rounds} rounds each using {threads} threads...")
        
        with Pool(threads) as pool:
            results = pool.map(play_match, tasks)
            
        # Tally results
        for n1, br1, n2, br2 in results:
            self.leaderboard[n1] += br1
            self.leaderboard[n2] += br2
            
        # Rank bots
        ranked = sorted(self.leaderboard.items(), key=lambda x: x[1], reverse=True)
        print("\n--- TOURNAMENT RESULTS ---")
        for i, (name, bankroll) in enumerate(ranked):
            print(f"{i+1}. {name}: {bankroll} chips")
            
        return ranked

if __name__ == "__main__":
    manager = TournamentManager('population.json', match_rounds=100) # Small test rounds if called directly
    manager.run_tournament()
