import random

class BaselinePlayer:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.tricks_won = 0
        self.collected_cards = []

    def add_cards(self, cards):
        self.hand.extend(cards)

    def clear_round_data(self):
        self.hand = []
        self.tricks_won = 0
        self.collected_cards = []

    def get_rank_value(self, rank):
        rank_order = ['1', 'R', 'D', 'V', '10', '9', '8', '7', '6', '5', '4', '3', '2']
        return rank_order.index(rank)

    def sort_hand(self):
        self.hand.sort(key=lambda c: self.get_rank_value(c['rank']))

    def filter_suit(self, suit):
        return [c for c in self.hand if c['suit'] == suit]

    def evaluate_trump_strength(self, trump_suit):
        trumps = self.filter_suit(trump_suit)
        if not trumps: return 0
        strong_trumps = [c for c in trumps if c['rank'] in ['1', 'R', 'D', 'V', '10']]
        return len(strong_trumps) * 2 + len(trumps)

    def decide_bid(self, trump_suit):
        # Implementation of your baseline ruleset logic
        strength = self.evaluate_trump_strength(trump_suit)
        return "ASK" if strength >= 6 else "PASS"

    def play_card(self, leading_suit, trump_suit, current_winning_card, is_leading):
        if is_leading:
            # Play best card if leading
            self.sort_hand()
            card = self.hand.pop(0)
            return card

        cards_in_suit = self.filter_suit(leading_suit)
        if cards_in_suit:
            cards_in_suit.sort(key=lambda c: self.get_rank_value(c['rank']))
            # Logic: Beat winner if possible, otherwise play worst of suit
            if self.can_beat(cards_in_suit[0], current_winning_card, trump_suit, leading_suit):
                card = cards_in_suit[0]
            else:
                card = cards_in_suit[-1]
            self.hand.remove(card)
            return card

        # No leading suit: Try trumping
        trump_cards = self.filter_suit(trump_suit)
        if trump_cards:
            trump_cards.sort(key=lambda c: self.get_rank_value(c['rank']))
            if not current_winning_card or current_winning_card['suit'] != trump_suit:
                card = trump_cards[0]
            elif self.can_beat(trump_cards[0], current_winning_card, trump_suit, leading_suit):
                card = trump_cards[0]
            else:
                self.sort_hand()
                card = self.hand.pop(-1)  # Worst card overall
                return card
            self.hand.remove(card)
            return card

        # Discard worst card
        self.sort_hand()
        return self.hand.pop(-1)

    def can_beat(self, card, winner, trump, lead):
        if not winner: return True
        if winner['suit'] == trump and card['suit'] != trump: return False
        if card['suit'] == trump and winner['suit'] != trump: return True
        if card['suit'] == winner['suit']:
            return self.get_rank_value(card['rank']) < self.get_rank_value(winner['rank'])
        return False