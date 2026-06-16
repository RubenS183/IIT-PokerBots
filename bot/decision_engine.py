import random
from poker_engine.monte_carlo import MonteCarloSimulator

class DecisionEngine:
    def __init__(self, params):
        self.params = params
        self.mc = MonteCarloSimulator()

    def get_action(self, state, hole_cards, known_opp_card, opp_model):
        win_prob = self.mc.estimate_win_prob(hole_cards, state.board, known_opp_card, num_sims=300)
        
        # Pot odds
        cost_to_call = state.opp_wager - state.my_wager
        
        if cost_to_call == 0:
            # We can check or raise
            if win_prob > self.params.get("value_bet_threshold", 0.65):
                if random.random() < self.params.get("slow_play_probability", 0.1):
                    return "check"
                return self._generate_raise(state, win_prob)
            
            # Bluffing
            if random.random() < self.params.get("bluff_probability", 0.1):
                return self._generate_raise(state, win_prob, is_bluff=True)
                
            return "check"
        else:
            # We are facing a bet. Call, raise or fold.
            pot_odds = cost_to_call / max(1, (state.pot + cost_to_call))
            
            # Adjust win_prob requirement based on opponent aggression
            adjusted_win_prob_req = pot_odds * self.params.get("fold_threshold", 1.0)
            
            if opp_model:
                # If opponent is very aggressive, we can loosen our calling requirements
                if opp_model.aggression_factor > 2.0:
                    adjusted_win_prob_req *= 0.8  # Call looser
            
            if win_prob > self.params.get("value_bet_threshold", 0.75):
                # Strong hand, might raise
                if random.random() < self.params.get("check_raise_frequency", 0.2):
                    return self._generate_raise(state, win_prob)
                return "call"
            
            if win_prob >= adjusted_win_prob_req:
                return "call"
                
            # Bluff raise?
            if random.random() < (self.params.get("bluff_probability", 0.1) * 0.5):
                return self._generate_raise(state, win_prob, is_bluff=True)
                
            return "fold"

    def _generate_raise(self, state, win_prob, is_bluff=False):
        # Determine raise size
        # Standard raise is 2.5x to 3x previous bet, or pot size
        base_pot = state.pot
        
        if is_bluff:
            raise_amt = int(base_pot * 0.5)
        else:
            agg = self.params.get("aggression_multiplier", 1.0)
            raise_amt = int(base_pot * 0.75 * agg)
            if win_prob > 0.85:
                # Very strong hand, value bet heavily
                raise_amt = int(base_pot * 1.5 * agg)
                
        # Calculate actual raise_to amount
        raise_to = state.my_wager + (state.opp_wager - state.my_wager) + raise_amt
        
        # Clamp to bounds
        raise_to = max(raise_to, state.min_raise_to)
        raise_to = min(raise_to, state.max_raise_to)
        
        if raise_to >= state.min_raise_to:
            return f"raise {int(raise_to)}"
        else:
            # If we cannot make a valid raise, we just call (or all-in if max_raise_to makes it valid but less than min_raise)
            # Actually, if max_raise_to < min_raise_to, we can raise all-in and it's valid
            if state.max_raise_to < state.min_raise_to:
                return f"raise {int(state.max_raise_to)}"
            return "call"
