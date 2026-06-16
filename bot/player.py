class GameState:
    def __init__(self, round_num, board, pot, chips, opp_chips, my_wager, opp_wager, min_raise_to, max_raise_to):
        self.round_num = round_num
        self.board = board
        self.pot = pot
        self.chips = chips
        self.opp_chips = opp_chips
        self.my_wager = my_wager
        self.opp_wager = opp_wager
        self.min_raise_to = min_raise_to
        self.max_raise_to = max_raise_to

class Player:
    def __init__(self, name="Bot"):
        self.name = name
        self.bankroll = 0.0
        self.chips = 0
        self.hole_cards = []
        self.known_opp_card = None

    def start_round(self, chips):
        self.chips = chips
        self.hole_cards = []
        self.known_opp_card = None

    def pre_round_state(self, is_sb):
        """Called to apply the SB or BB before round truly begins"""
        pass

    def get_action(self, state: GameState) -> str:
        """
        Returns:
            'fold'
            'check'
            'call'
            'raise <amount>' (where amount is the *raise to* amount)
        """
        raise NotImplementedError

    def get_bid(self, state: GameState) -> int:
        """
        Returns: integer bid amount
        """
        raise NotImplementedError

    def receive_info(self, opp_card):
        self.known_opp_card = opp_card

    def end_round(self, chip_delta):
        self.bankroll += chip_delta
