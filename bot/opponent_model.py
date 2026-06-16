class OpponentModel:
    def __init__(self):
        self.hands_played = 0
        self.vpip_count = 0 
        self.preflop_raises = 0
        self.postflop_bets = 0
        self.postflop_calls = 0
        self.total_bids = 0
        self.auction_wins = 0

    def start_hand(self):
        self.hands_played += 1
        self.put_in_pot = False

    def observe_action(self, action_type, round_type, amt=0):
        # action_type: 'call', 'raise', 'check', 'fold'
        if action_type in ['call', 'raise']:
            if not self.put_in_pot:
                self.vpip_count += 1
                self.put_in_pot = True
        
        if action_type == 'raise':
            if round_type == 'preflop':
                self.preflop_raises += 1
            else:
                self.postflop_bets += 1
        elif action_type == 'call' and round_type != 'preflop':
            self.postflop_calls += 1

    def observe_auction(self, opp_bid, won):
        self.total_bids += opp_bid
        if won:
            self.auction_wins += 1

    @property
    def vpip(self):
        return self.vpip_count / max(1, self.hands_played)

    @property
    def aggression_factor(self):
        # (Raises + Bets) / Calls
        calls = max(1, self.postflop_calls)
        return self.postflop_bets / calls

    @property
    def avg_bid(self):
        return self.total_bids / max(1, self.hands_played)
