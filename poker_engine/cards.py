from treys import Card, Deck

# Using the treys Card and Deck classes directly.
# Card.new('Ah') creates an integer representation.
# Card.int_to_str(card_int) prints standard format.
# Card.get_rank_int(card_int) gets standard 0-12 rank.
# Card.get_suit_int(card_int) gets standard 0-3 suit.

__all__ = ["Card", "Deck"]
