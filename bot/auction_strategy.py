from poker_engine.monte_carlo import MonteCarloSimulator

class AuctionStrategy:
    def __init__(self, bid_multiplier=1.0, base_bid_fraction=0.1):
        self.bid_multiplier = bid_multiplier
        self.base_bid_fraction = base_bid_fraction
        self.mc = MonteCarloSimulator()

    def calculate_bid(self, state, hole_cards, opp_model=None):
        # Expected Value of Information Strategy
        # EVI = (P(Win|Info) - P(Win)) * Pot
        
        # Estimate P(Win) without info
        p_win_no_info = self.mc.estimate_win_prob(hole_cards, state.board, None, num_sims=300)
        
        # We can't actually calculate P(Win|Info) deterministically without knowing the card.
        # But heuristically: Information is more valuable when the hand is marginal (P(Win) ~ 0.5)
        # Information is less valuable when we have exactly the nuts or nothing.
        
        uncertainty = 1.0 - 4.0 * ((p_win_no_info - 0.5) ** 2) # Parabola peaking at 0.5
        
        # Rough EVI approximation
        evi_approximation = state.pot * 0.15 * uncertainty * self.bid_multiplier
        
        # Add a baseline fraction to just win the info
        base_bid = state.pot * self.base_bid_fraction
        
        target_bid = int(evi_approximation + base_bid)
        
        # Clamp to reasonable limits based on stack
        max_safe_bid = int(state.chips * 0.5) # Never bid more than half our stack generally
        
        target_bid = min(target_bid, max_safe_bid)
        target_bid = min(target_bid, state.chips) # Hard cap at our chips
        
        return target_bid
