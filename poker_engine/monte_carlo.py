import random
from treys import Deck
from .evaluator import EngineEvaluator

class MonteCarloSimulator:
    def __init__(self):
        self.evaluator = EngineEvaluator()
        self.full_deck_cached = Deck.GetFullDeck()

    def estimate_win_prob(self, hole_cards, board_cards, opp_known_card=None, num_sims=500):
        """
        Estimates the win probability of the current hand.
        hole_cards: List[int] (2 cards)
        board_cards: List[int] (0 to 5 cards)
        opp_known_card: int or None (if we won the Sneak Peek auction)
        num_sims: int (number of random rollouts)
        """
        wins = 0
        ties = 0

        known_cards = set(hole_cards) | set(board_cards)
        if opp_known_card is not None:
            known_cards.add(opp_known_card)

        available_cards = [c for c in self.full_deck_cached if c not in known_cards]
        num_board_needed = 5 - len(board_cards)

        for _ in range(num_sims):
            # We only need enough cards for the opponent and the board.
            # Using random.sample is usually faster than shuffling the whole deck.
            cards_needed = num_board_needed + (1 if opp_known_card is not None else 2)
            sampled = random.sample(available_cards, cards_needed)
            
            idx = 0
            if opp_known_card is not None:
                opp_hole = [opp_known_card, sampled[idx]]
                idx += 1
            else:
                opp_hole = [sampled[idx], sampled[idx+1]]
                idx += 2
                
            sim_board = board_cards + sampled[idx:idx+num_board_needed]

            my_score = self.evaluator.evaluate(sim_board, hole_cards)
            opp_score = self.evaluator.evaluate(sim_board, opp_hole)

            # In treys, lower score is better
            if my_score < opp_score:
                wins += 1
            elif my_score == opp_score:
                ties += 1

        return (wins + 0.5 * ties) / num_sims
