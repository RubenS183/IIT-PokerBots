from bot.player import Player
from bot.opponent_model import OpponentModel
from bot.auction_strategy import AuctionStrategy
from bot.decision_engine import DecisionEngine

class ParameterizedBot(Player):
    def __init__(self, name="Bot", params=None):
        super().__init__(name)
        if params is None:
            params = {
                "aggression_multiplier": 1.0,
                "bluff_probability": 0.1,
                "value_bet_threshold": 0.65,
                "auction_base_bid_fraction": 0.05,
                "auction_bid_multiplier": 1.0,
                "fold_threshold": 1.0,
                "slow_play_probability": 0.1,
                "check_raise_frequency": 0.1
            }
        self.params = params
        self.opp_model = OpponentModel()
        self.auction_strategy = AuctionStrategy(
            bid_multiplier=params.get("auction_bid_multiplier", 1.0),
            base_bid_fraction=params.get("auction_base_bid_fraction", 0.05)
        )
        self.decision_engine = DecisionEngine(self.params)
        
    def start_round(self, chips):
        super().start_round(chips)
        self.opp_model.start_hand()
        # In a real engine, we would parse history here to update opp_model.
        # For our simple framework, we will just rely on the Game to feed us actions if we implement listeners.
        # But we can also just let the bot track its own actions? 
        # Actually our Game framework doesn't currently broadcast actions back natively.
        # For simplicity and speed, opponents are treated statically in pure self-play 
        # unless we explicitly pass history to track. We will just use the default opp_model for now.
        
    def get_action(self, state):
        return self.decision_engine.get_action(state, self.hole_cards, self.known_opp_card, self.opp_model)

    def get_bid(self, state):
        return self.auction_strategy.calculate_bid(state, self.hole_cards, self.opp_model)
