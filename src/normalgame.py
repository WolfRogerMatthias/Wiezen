import json
import random

random.seed(42)


def loading_deck():
    with open('deck.json', 'r') as f:
        deck = json.load(f)
    return deck


def initial_deck():
    deck = loading_deck()
    cards = deck['cards']
    random.shuffle(cards)
    cut = random.randint(1, len(cards) - 1)
    cards = cards[cut:] + cards[:cut]
    return cards


def cut_deck(cards):
    """Cut the deck without shuffling"""
    cut = random.randint(1, len(cards) - 1)
    cards = cards[cut:] + cards[:cut]
    return cards


def deal_deck(cards, players):
    card_deal = [4, 4, 5]  # rounds: 4, 4, 5 cards per player
    player_names = list(players.keys())
    card_index = 0

    for round_cards in card_deal:
        for player in player_names:
            # Give the next 'round_cards' number of cards to this player
            players[player].extend(cards[card_index:card_index + round_cards])
            card_index += round_cards
    return players


def get_rank_value(rank):
    """Get numeric value for a rank (lower is better)"""
    rank_order = ['1', 'R', 'D', 'V', '10', '9', '8', '7', '6', '5', '4', '3', '2']
    rank_value = {rank: i for i, rank in enumerate(rank_order)}
    return rank_value[rank]


def sort_cards(cards):
    # Define your custom rank order (highest first)
    sorted_cards = sorted(cards, key=lambda c: get_rank_value(c['rank']))
    return sorted_cards


def best_card(cards):
    sorted_cards = sort_cards(cards)
    return sorted_cards[0]


def worst_card(cards):
    sorted_cards = sort_cards(cards)
    return sorted_cards[-1]


def filter_cards_by_suit(cards, suit):
    """Return all cards that match the given suit"""
    return [card for card in cards if card['suit'] == suit]


def get_current_winning_card(dealt_cards, leading_suit):
    """Get the currently winning card from the dealt cards"""
    leading_suit_cards = [card for card in dealt_cards if card['suit'] == leading_suit]
    if not leading_suit_cards:
        return None
    return best_card(leading_suit_cards)


def can_beat_current_winner(card, current_winner):
    """Check if a card can beat the current winning card"""
    if current_winner is None:
        return True
    return get_rank_value(card['rank']) < get_rank_value(current_winner['rank'])


def get_round_winner(dealt_cards, player_order, leading_suit):
    """Determine the winner of the round based on highest card of leading suit"""
    best_card_index = -1
    best_rank_value = float('inf')

    for i, (player, card) in enumerate(zip(player_order, dealt_cards)):
        # Only consider cards that match the leading suit
        if card['suit'] == leading_suit:
            if get_rank_value(card['rank']) < best_rank_value:
                best_rank_value = get_rank_value(card['rank'])
                best_card_index = i

    return player_order[best_card_index]


def rotate_player_order(player_names, starting_player):
    """Rotate player order so starting_player starts"""
    start_index = player_names.index(starting_player)
    return player_names[start_index:] + player_names[:start_index]


def play_game_round(cards, game_round_number, starting_player):
    """Play one complete game round (13 turns)"""
    print(f"\n{'#' * 60}")
    print(f"# GAME ROUND {game_round_number}")
    print(f"# Starting player: {starting_player}")
    print(f"{'#' * 60}")

    players = {"player1": [], "player2": [], "player3": [], "player4": []}
    players = deal_deck(cards, players)
    print("\nInitial hands:")
    for player, hand in players.items():
        print(f"{player}: {len(hand)} cards")

    # Set initial player order based on starting player
    all_players = ["player1", "player2", "player3", "player4"]
    player_names = rotate_player_order(all_players, starting_player)

    rounds_won = {player: 0 for player in all_players}
    collected_cards = {player: [] for player in all_players}  # Track collected card stacks

    # Play 13 turns
    for i in range(13):
        print(f"\n{'=' * 60}")
        print(f"Turn {i + 1}:")
        print(f"Play order: {' -> '.join(player_names)}")
        dealt_cards = []
        leading_suit = None

        for j, player in enumerate(player_names):
            player_hand = players[player]

            if j == 0:
                # First player plays their best card
                card_to_play = best_card(player_hand)
                leading_suit = card_to_play['suit']
                print(f"Leading suit: {leading_suit}")
            else:
                # Other players must follow suit if possible
                cards_in_suit = filter_cards_by_suit(player_hand, leading_suit)

                if cards_in_suit:
                    # Has cards in leading suit - check if can beat current winner
                    current_winner = get_current_winning_card(dealt_cards, leading_suit)
                    best_in_suit = best_card(cards_in_suit)

                    if can_beat_current_winner(best_in_suit, current_winner):
                        # Can win - play best card in suit
                        card_to_play = best_in_suit
                        print(f"{player} can beat current winner, playing best card in suit")
                    else:
                        # Can't win - play worst card in suit to save better cards
                        card_to_play = worst_card(cards_in_suit)
                        print(f"{player} can't beat current winner, playing worst card in suit")
                else:
                    # No cards in leading suit - play worst card overall
                    card_to_play = worst_card(player_hand)
                    print(f"{player} has no cards in leading suit, playing worst card overall")

            print(f"{player}: {card_to_play}")
            players[player].remove(card_to_play)
            dealt_cards.append(card_to_play)

        # Determine winner
        winner = get_round_winner(dealt_cards, player_names, leading_suit)
        rounds_won[winner] += 1

        # Winner collects all 4 cards in random order
        random.shuffle(dealt_cards)
        collected_cards[winner].extend(dealt_cards)

        print(f"\n🏆 {winner} wins this turn and collects 4 cards!")
        print(f"Current score: {rounds_won}")

        # Rotate player order for next turn
        player_names = rotate_player_order(all_players, winner)

    print(f"\n{'=' * 60}")
    print(f"GAME ROUND {game_round_number} COMPLETE!")
    print(f"Final scores: {rounds_won}")
    print(f"\nCards collected by each player:")
    for player in collected_cards:
        print(f"{player}: {len(collected_cards[player])} cards")

    return rounds_won, collected_cards


def reassemble_deck(collected_cards):
    """Reassemble deck from collected cards - stacks stay together but order is randomized"""
    player_names = list(collected_cards.keys())

    # Each player's collected cards are divided into stacks of 4
    all_stacks = []
    for player in player_names:
        cards = collected_cards[player]
        # Create stacks of 4 cards (each stack stays in the order collected)
        for i in range(0, len(cards), 4):
            stack = cards[i:i + 4]
            all_stacks.append(stack)

    # Randomly shuffle the order of stacks
    random.shuffle(all_stacks)

    # Flatten the stacks back into a single deck
    reassembled = []
    for stack in all_stacks:
        reassembled.extend(stack)

    # Cut the deck (no shuffling)
    reassembled = cut_deck(reassembled)

    print(f"\n{'*' * 60}")
    print("Deck reassembled: 13 stacks of 4 cards shuffled and cut")
    print(f"Total cards: {len(reassembled)}")
    print(f"{'*' * 60}")

    return reassembled


def game():
    """Main game function - plays 2 complete rounds"""
    # Initialize deck for first round
    cards = initial_deck()

    total_rounds_won = {"player1": 0, "player2": 0, "player3": 0, "player4": 0}

    # Starting player rotates each game round
    all_players = ["player1", "player2", "player3", "player4"]

    # Play 2 game rounds
    for game_round in range(1, 10):
        # Determine starting player (rotates: player1, player2, player3, player4, player1, ...)
        starting_player = all_players[(game_round - 1) % 4]

        rounds_won, collected_cards = play_game_round(cards, game_round, starting_player)

        # Add to total
        for player, wins in rounds_won.items():
            total_rounds_won[player] += wins

        # Reassemble deck for next round (if not last round)

        cards = reassemble_deck(collected_cards)

    # Final summary
    print(f"\n{'#' * 60}")
    print("# FINAL SUMMARY")
    print(f"{'#' * 60}")
    print(f"\nTotal turns won across both game rounds:")
    for player, wins in sorted(total_rounds_won.items(), key=lambda x: x[1], reverse=True):
        print(f"{player}: {wins} turns")

    winner = max(total_rounds_won, key=total_rounds_won.get)
    print(f"\n🎉 OVERALL WINNER: {winner} with {total_rounds_won[winner]} turns won! 🎉")


if __name__ == "__main__":
    game()