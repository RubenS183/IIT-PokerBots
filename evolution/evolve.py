import json
import random
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolution.generator import generate_base_population
from evolution.tournament import TournamentManager

def mutate_param(val, min_val, max_val):
    # Mutate by normally distributed factor centered at 1.0 with 0.15 std_dev
    factor = random.gauss(1.0, 0.15)
    new_val = val * factor
    
    # Optional small chance to randomize completely
    if random.random() < 0.05:
        new_val = random.uniform(min_val, max_val)
        
    return max(min_val, min(max_val, new_val))

def mutate_bot(base_params):
    return {
        "aggression_multiplier": mutate_param(base_params["aggression_multiplier"], 0.2, 5.0),
        "bluff_probability": mutate_param(base_params["bluff_probability"], 0.0, 0.9),
        "value_bet_threshold": mutate_param(base_params["value_bet_threshold"], 0.4, 0.95),
        "auction_base_bid_fraction": mutate_param(base_params["auction_base_bid_fraction"], 0.0, 0.5),
        "auction_bid_multiplier": mutate_param(base_params["auction_bid_multiplier"], 0.0, 5.0),
        "fold_threshold": mutate_param(base_params["fold_threshold"], 0.5, 2.0),
        "slow_play_probability": mutate_param(base_params["slow_play_probability"], 0.0, 0.5),
        "check_raise_frequency": mutate_param(base_params["check_raise_frequency"], 0.0, 0.5)
    }

def run_evolution(generations=10, population_size=30, match_rounds=10000):
    pop_file = 'population.json'
    
    # Gen 0
    if not os.path.exists(pop_file):
        generate_base_population(size=population_size, filename=pop_file)
        
    for gen in range(1, generations + 1):
        print(f"\n{'='*40}\nGENERATION {gen}\n{'='*40}")
        
        # 1. Evaluate
        manager = TournamentManager(pop_file, match_rounds=match_rounds)
        ranked = manager.run_tournament()
        
        # 2. Select Top 5
        top_5_names = [name for name, score in ranked[:5]]
        
        with open(pop_file, 'r') as f:
            population = json.load(f)
            
        top_5_params = [population[name] for name in top_5_names]
        
        print("\nTop 5 Bots this generation:")
        for name, score in ranked[:5]:
            print(f" {name}: {score} chips")
            
        if gen == generations:
            print("\nEvolution complete.")
            with open('best_bot.json', 'w') as f:
                json.dump(top_5_params[0], f, indent=4)
            print("Best bot saved as best_bot.json")
            break
            
        # 3. Create Next Generation
        next_gen = {}
        # Elitism: keep Top 5 unmodified
        for i, params in enumerate(top_5_params):
            next_gen[f"bot_gen{gen}_elite_{i}"] = params
            
        # Mutate the rest
        for i in range(5, population_size):
            parent = random.choice(top_5_params)
            next_gen[f"bot_gen{gen}_mut_{i}"] = mutate_bot(parent)
            
        with open(pop_file, 'w') as f:
            json.dump(next_gen, f, indent=4)

if __name__ == "__main__":
    # In a real run, match_rounds=10000
    # For testing framework functionality, defaulting to match_rounds=10
    run_evolution(generations=10, population_size=30, match_rounds=10)
