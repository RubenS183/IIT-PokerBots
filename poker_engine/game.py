import random
from bot.player import GameState
from .cards import Deck
from .evaluator import EngineEvaluator

class SneakPeekGame:
    def __init__(self, p1, p2, rounds=1000, starting_chips=5000, sb=10, bb=20):
        self.p1 = p1
        self.p2 = p2
        self.rounds = rounds
        self.starting_chips = starting_chips
        self.sb = sb
        self.bb = bb
        self.evaluator = EngineEvaluator()

    def run(self):
        for r in range(1, self.rounds + 1):
            if r % 2 != 0:
                p_sb, p_bb = self.p1, self.p2
            else:
                p_sb, p_bb = self.p2, self.p1
            
            self._play_round(r, p_sb, p_bb)

    def _play_round(self, round_num, p_sb, p_bb):
        p_sb.start_round(self.starting_chips)
        p_bb.start_round(self.starting_chips)

        deck = Deck()
        deck.shuffle()

        p_sb.hole_cards = [deck.draw(1)[0], deck.draw(1)[0]]
        p_bb.hole_cards = [deck.draw(1)[0], deck.draw(1)[0]]

        pot = 0
        
        # Post Blinds
        sb_amt = min(self.sb, p_sb.chips)
        bb_amt = min(self.bb, p_bb.chips)
        
        p_sb.chips -= sb_amt
        p_bb.chips -= bb_amt
        
        p_sb_wager = sb_amt
        p_bb_wager = bb_amt

        board = []
        
        # State object helper
        def make_state(p_acting, p_waiting, w_acting, w_waiting):
            cost_to_call = w_waiting - w_acting
            
            # Minimum Raise = Current Wager + Cost to Call + max(Big Blind, Cost to Call)
            # Since amount is "Raise To" which includes current wager:
            min_raise_to = w_acting + cost_to_call + max(self.bb, cost_to_call)
            max_raise_to = w_acting + min(p_acting.chips, p_waiting.chips + cost_to_call) # The max amount the pot can see from this player
            
            # Bound minimum by max
            if min_raise_to > max_raise_to:
                min_raise_to = max_raise_to

            return GameState(
                round_num, board.copy(), pot + p_sb_wager + p_bb_wager,
                p_acting.chips, p_waiting.chips,
                w_acting, w_waiting,
                min_raise_to, max_raise_to
            )

        def betting_round(first_actor='sb'):
            nonlocal p_sb_wager, p_bb_wager
            
            # If someone is all-in, betting ends (should check if both have chips)
            if p_sb.chips == 0 or p_bb.chips == 0:
                return 'continue'
                
            active = p_sb if first_actor == 'sb' else p_bb
            waiting = p_bb if first_actor == 'sb' else p_sb
            
            w_active = p_sb_wager if active == p_sb else p_bb_wager
            w_waiting = p_bb_wager if waiting == p_sb else p_sb_wager

            action_count = 0
            
            while True:
                # If someone is all-in, resolve the loop (should not occur if we started with chips > 0 but valid as break cond)
                if active.chips == 0 and w_active == w_waiting:
                    break

                state = make_state(active, waiting, w_active, w_waiting)
                try:
                    action_str = active.get_action(state).strip().lower()
                except Exception:
                    action_str = "fold"

                if action_str == "fold":
                    return 'fold_' + ('sb' if active == p_sb else 'bb')

                elif action_str == "check":
                    if w_active < w_waiting: # Invalid check, treat as fold
                        return 'fold_' + ('sb' if active == p_sb else 'bb')
                    action_count += 1
                    if action_count >= 2:
                        break # Both checked, or checked down

                elif action_str == "call":
                    call_amt = w_waiting - w_active
                    call_amt = min(call_amt, active.chips)
                    active.chips -= call_amt
                    w_active += call_amt
                    action_count += 1
                    if w_active == w_waiting and action_count >= 2:
                        break # Call closes action

                elif action_str.startswith("raise"):
                    try:
                        raise_to = int(action_str.split()[1])
                    except:
                        return 'fold_' + ('sb' if active == p_sb else 'bb')

                    # Validate max
                    max_cap = w_active + active.chips
                    max_cap_opp = w_waiting + waiting.chips
                    raise_to = min(raise_to, max_cap, max_cap_opp)
                    
                    if raise_to < state.min_raise_to and raise_to != min(max_cap, max_cap_opp):
                        return 'fold_' + ('sb' if active == p_sb else 'bb')

                    raise_amt = raise_to - w_active
                    if raise_amt < 0 or raise_amt > active.chips:
                        return 'fold_' + ('sb' if active == p_sb else 'bb')
                        
                    active.chips -= raise_amt
                    w_active += raise_amt
                    action_count = 1 # Opponent now has 1 action to respond
                else:
                    return 'fold_' + ('sb' if active == p_sb else 'bb')

                # Swap roles
                if active == p_sb:
                    p_sb_wager = w_active
                    active = p_bb
                    waiting = p_sb
                    w_active = p_bb_wager
                    w_waiting = p_sb_wager
                else:
                    p_bb_wager = w_active
                    active = p_sb
                    waiting = p_bb
                    w_active = p_sb_wager
                    w_waiting = p_bb_wager
                    
            if active == p_sb:
                # Need to write back wager
                return 'continue'
            else:
                return 'continue'

        # Pre-flop (SB acts first)
        res = betting_round('sb')
        pot += p_sb_wager + p_bb_wager
        p_sb_wager = 0
        p_bb_wager = 0
        if res.startswith('fold'):
            self._handle_fold(res, p_sb, p_bb, pot)
            return

        # Flop
        board.extend(deck.draw(3))

        # AUCTION (Sneak Peek)
        sb_bid = 0
        bb_bid = 0
        if p_sb.chips > 0 and p_bb.chips > 0:
            try:
                sb_bid = max(0, min(p_sb.chips, p_sb.get_bid(make_state(p_sb, p_bb, 0, 0))))
            except: sb_bid = 0
            try:
                bb_bid = max(0, min(p_bb.chips, p_bb.get_bid(make_state(p_bb, p_sb, 0, 0))))
            except: bb_bid = 0

            if sb_bid > bb_bid:
                p_sb.chips -= bb_bid
                pot += bb_bid
                p_sb.receive_info(random.choice(p_bb.hole_cards))
            elif bb_bid > sb_bid:
                p_bb.chips -= sb_bid
                pot += sb_bid
                p_bb.receive_info(random.choice(p_sb.hole_cards))
            else:
                p_sb.chips -= sb_bid
                p_bb.chips -= bb_bid
                pot += (sb_bid + bb_bid)
                p_sb.receive_info(random.choice(p_bb.hole_cards))
                p_bb.receive_info(random.choice(p_sb.hole_cards))

        res = betting_round('bb')
        pot += p_sb_wager + p_bb_wager
        p_sb_wager = 0
        p_bb_wager = 0
        if res.startswith('fold'):
            self._handle_fold(res, p_sb, p_bb, pot)
            return

        # Turn
        board.append(deck.draw(1)[0])
        res = betting_round('bb')
        pot += p_sb_wager + p_bb_wager
        p_sb_wager = 0
        p_bb_wager = 0
        if res.startswith('fold'):
            self._handle_fold(res, p_sb, p_bb, pot)
            return

        # River
        board.append(deck.draw(1)[0])
        res = betting_round('bb')
        pot += p_sb_wager + p_bb_wager
        p_sb_wager = 0
        p_bb_wager = 0
        if res.startswith('fold'):
            self._handle_fold(res, p_sb, p_bb, pot)
            return

        # Showdown
        sb_score = self.evaluator.evaluate(board, p_sb.hole_cards)
        bb_score = self.evaluator.evaluate(board, p_bb.hole_cards)

        if sb_score < bb_score:
            sb_delta = pot - (self.starting_chips - p_sb.chips)
            bb_delta = -(self.starting_chips - p_bb.chips)
        elif bb_score < sb_score:
            bb_delta = pot - (self.starting_chips - p_bb.chips)
            sb_delta = -(self.starting_chips - p_sb.chips)
        else:
            half = pot / 2.0
            sb_delta = half - (self.starting_chips - p_sb.chips)
            bb_delta = half - (self.starting_chips - p_bb.chips)

        p_sb.end_round(sb_delta)
        p_bb.end_round(bb_delta)

    def _handle_fold(self, fold_str, p_sb, p_bb, pot):
        if fold_str == 'fold_sb':
            sb_delta = -(self.starting_chips - p_sb.chips)
            bb_delta = pot - (self.starting_chips - p_bb.chips)
        else:
            bb_delta = -(self.starting_chips - p_bb.chips)
            sb_delta = pot - (self.starting_chips - p_sb.chips)
            
        p_sb.end_round(sb_delta)
        p_bb.end_round(bb_delta)
