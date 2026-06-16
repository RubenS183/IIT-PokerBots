from treys import Card, Evaluator, Deck

# Wrap or simply expose treys functionality for the rest of the engine to import safely.

class EngineEvaluator:
    def __init__(self):
        self.evaluator = Evaluator()

    def evaluate(self, board, hand):
        """
        Evaluates the hand given the board.
        In treys, lower rank is better.
        1 is Royal Flush, 7462 is the worst high card.
        """
        return self.evaluator.evaluate(board, hand)

    def get_rank_class(self, score):
        return self.evaluator.get_rank_class(score)

    def class_to_string(self, rank_class):
        return self.evaluator.class_to_string(rank_class)
