import json
import random

def generate_base_population(size=30, filename='population.json'):
    bots = {}
    
    # Generate varied archetype families
    for i in range(size):
        archetype = i % 7
        
        if archetype == 0: # Tight-Aggressive
            bots[f"bot_gen0_TA_{i}"] = {
                "aggression_multiplier": random.uniform(2.0, 3.0),
                "bluff_probability": random.uniform(0.05, 0.15),
                "value_bet_threshold": random.uniform(0.75, 0.90),
                "auction_base_bid_fraction": random.uniform(0.01, 0.05),
                "auction_bid_multiplier": random.uniform(0.8, 1.2),
                "fold_threshold": random.uniform(1.0, 1.2),
                "slow_play_probability": random.uniform(0.05, 0.15),
                "check_raise_frequency": random.uniform(0.1, 0.25)
            }
        elif archetype == 1: # Loose-Aggressive
            bots[f"bot_gen0_LA_{i}"] = {
                "aggression_multiplier": random.uniform(2.5, 4.0),
                "bluff_probability": random.uniform(0.25, 0.45),
                "value_bet_threshold": random.uniform(0.55, 0.70),
                "auction_base_bid_fraction": random.uniform(0.05, 0.1),
                "auction_bid_multiplier": random.uniform(1.0, 1.5),
                "fold_threshold": random.uniform(0.8, 1.0),
                "slow_play_probability": random.uniform(0.0, 0.1),
                "check_raise_frequency": random.uniform(0.2, 0.4)
            }
        elif archetype == 2: # Tight-Passive
            bots[f"bot_gen0_TP_{i}"] = {
                "aggression_multiplier": random.uniform(0.5, 1.2),
                "bluff_probability": random.uniform(0.0, 0.05),
                "value_bet_threshold": random.uniform(0.8, 0.95),
                "auction_base_bid_fraction": random.uniform(0.0, 0.03),
                "auction_bid_multiplier": random.uniform(0.5, 0.8),
                "fold_threshold": random.uniform(1.2, 1.5),
                "slow_play_probability": random.uniform(0.1, 0.3),
                "check_raise_frequency": random.uniform(0.0, 0.1)
            }
        elif archetype == 3: # Bluff-Heavy
            bots[f"bot_gen0_BH_{i}"] = {
                "aggression_multiplier": random.uniform(1.5, 3.0),
                "bluff_probability": random.uniform(0.5, 0.8),
                "value_bet_threshold": random.uniform(0.6, 0.8),
                "auction_base_bid_fraction": random.uniform(0.05, 0.15),
                "auction_bid_multiplier": random.uniform(1.2, 1.8),
                "fold_threshold": random.uniform(0.9, 1.1),
                "slow_play_probability": random.uniform(0.0, 0.05),
                "check_raise_frequency": random.uniform(0.3, 0.5)
            }
        elif archetype == 4: # Auction-Sniper
            bots[f"bot_gen0_AS_{i}"] = {
                "aggression_multiplier": random.uniform(1.0, 2.0),
                "bluff_probability": random.uniform(0.1, 0.2),
                "value_bet_threshold": random.uniform(0.65, 0.8),
                "auction_base_bid_fraction": random.uniform(0.2, 0.35),
                "auction_bid_multiplier": random.uniform(2.5, 4.0),
                "fold_threshold": random.uniform(0.9, 1.1),
                "slow_play_probability": random.uniform(0.1, 0.2),
                "check_raise_frequency": random.uniform(0.1, 0.2)
            }
        else: # Randomized generic / GTO approximator
            bots[f"bot_gen0_GTO_{i}"] = {
                "aggression_multiplier": random.uniform(1.0, 2.5),
                "bluff_probability": random.uniform(0.1, 0.3),
                "value_bet_threshold": random.uniform(0.6, 0.85),
                "auction_base_bid_fraction": random.uniform(0.02, 0.12),
                "auction_bid_multiplier": random.uniform(0.8, 2.0),
                "fold_threshold": random.uniform(0.9, 1.2),
                "slow_play_probability": random.uniform(0.05, 0.2),
                "check_raise_frequency": random.uniform(0.1, 0.3)
            }

    with open(filename, 'w') as f:
        json.dump(bots, f, indent=4)
        
    print(f"Generated {size} bots in {filename}")

if __name__ == "__main__":
    generate_base_population()
