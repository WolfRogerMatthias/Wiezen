import random

from .DeckLoader import DeckLoader
from .Players import BaselinePlayer

class Game:
    def __init__(self):
        self.loader = DeckLoader()
        self.players = [BaselinePlayer(f"Player {i+1}") for i in range(4)]
        self.total_points = {p.name: 0 for p in self.players}
        self.target_score = 9

    def run(self):
        game_round = 1
        current_deck = self.loader.cards  # Initial deck from JSON

        while max(self.total_points.values()) < self.target_score:
            print(f"\n--- ROUND {game_round} ---")
            starting_idx = (game_round - 1) % 4
            round_points, collected_deck = self.play_round(current_deck, starting_idx)

            for name, pts in round_points.items():
                self.total_points[name] += pts

            print(f"Current Scores: {self.total_points}")
            current_deck = self.reassemble_deck(collected_deck)
            game_round += 1

        winner = max(self.total_points, key=self.total_points.get)
        print(f"\nOVERALL WINNER: {winner}!")

    def play_round(self, deck, starting_idx):
        # 4-4-5 Dealing logic
        random.shuffle(deck)
        for count in [4, 4, 5]:
            for i in range(4):
                idx = (starting_idx + i) % 4
                self.players[idx].add_cards(deck[:count])
                deck = deck[count:]

        trump_card = deck[-1] if deck else self.players[3].hand[-1]
        trump_suit = trump_card['suit']
        print(f"Trump is {trump_suit} (Card: {trump_card['rank']})")

        # Bidding
        askers = []
        for i in range(4):
            p = self.players[(starting_idx + i) % 4]
            if p.decide_bid(trump_suit) == "ASK":
                askers.append(p)
                if len(askers) == 2: break

        mode, team, opponents = self.determine_mode(askers)
        if mode == "REDEAL":
            print("No one played. Redealing...")
            for p in self.players: p.clear_round_data()
            return {p.name: 0 for p in self.players}, deck

        # Play 13 Tricks
        lead_player_idx = starting_idx
        for _ in range(13):
            trick = []
            current_winner_card = None

            # Rotation for the trick
            for i in range(4):
                p_idx = (lead_player_idx + i) % 4
                p = self.players[p_idx]
                is_leading = (i == 0)
                lead_suit = trick[0][1]['suit'] if not is_leading else None

                card = p.play_card(lead_suit, trump_suit, current_winner_card, is_leading)
                trick.append((p, card))

                if is_leading or p.can_beat(card, current_winner_card, trump_suit, lead_suit):
                    current_winner_card = card
                    winner_of_trick = p

            winner_of_trick.tricks_won += 1
            winner_of_trick.collected_cards.extend([c for p, c in trick])
            # Winner leads next trick
            lead_player_idx = self.players.index(winner_of_trick)

        points = self.calculate_points(mode, team, opponents)

        # Collect cards for next round
        all_collected = []
        for p in self.players:
            all_collected.extend(p.collected_cards)
            p.clear_round_data()

        return points, all_collected

    def determine_mode(self, askers):
        if not askers: return "REDEAL", [], []
        if len(askers) == 1:
            # Logic from normalgame: Solo if strength >= 10
            return ("SOLO", [askers[0]], [p for p in self.players if p != askers[0]])
        return ("TEAM", askers, [p for p in self.players if p not in askers])

    def calculate_points(self, mode, team, opponents):
        pts = {p.name: 0 for p in self.players}

        # Total tricks won by the bidding side (could be 1 or 2 players)
        wins = sum(p.tricks_won for p in team)

        if mode == "TEAM":
            # Rule: 'fragen und mitgehen' (2 vs. 2)
            # Target is 8 tricks. Base points: 2. Each extra trick: +1.
            target = 8
            if wins >= target:
                # Winners get 2 + (extra tricks)
                base_val = 2 + (wins - target)
            else:
                # Losers pay the amount they failed to reach
                # If they get 7 tricks, they are -1 from target, so they lose 2 (base) + 1 (missing)
                base_val = -(2 + (target - wins))

            # Distribution: Each winner gets base_val, each opponent pays base_val
            for p in team: pts[p.name] = base_val
            for p in opponents: pts[p.name] = -base_val

        elif mode == "SOLO":
            # Rule: 'alleine gehen' (1 vs. 3)
            # Target is 5 tricks. Base points: 6. Each extra trick: +3 (1 from each opponent).
            target = 5
            if wins >= target:
                # Solo player gets 6 + 3 for every trick over 5
                # (Note: The PDF says 6 pts + 3/extra, which means +1 from each of the 3 opponents)
                total_win_from_all = 6 + (3 * (wins - target))
            else:
                # Solo player pays 6 + 3 for every trick they are under 5
                total_win_from_all = -(6 + (3 * (target - wins)))

            # The Solo player (team[0]) receives/pays the total amount.
            # The three opponents split the cost/gain equally.
            solo_player = team[0]
            pts[solo_player.name] = total_win_from_all
            for p in opponents:
                pts[p.name] = -(total_win_from_all / 3)

        return pts

    def reassemble_deck(self, cards):
        # Keeps stacks together then cuts
        cut = random.randint(1, len(cards) - 1)
        return cards[cut:] + cards[:cut]