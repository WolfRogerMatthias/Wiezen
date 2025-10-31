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


def determine_trump_suit(cards):
    """Determine trump suit from the last card in the deck"""
    trump_card = cards[-1]
    trump_suit = trump_card['suit']
    print(f"🃏 Trump card is: {trump_card['rank']} of {trump_suit}")
    print(f"🎯 Trump suit for this round: {trump_suit}")
    return trump_suit


def evaluate_trump_strength(hand, trump_suit):
    """Evaluate how good a player's trump cards are"""
    trump_cards = filter_cards_by_suit(hand, trump_suit)
    if not trump_cards:
        return 0
    
    # Count strong trump cards (1, R, D, V, 10)
    strong_trumps = [card for card in trump_cards if card['rank'] in ['1', 'R', 'D', 'V', '10']]
    total_trumps = len(trump_cards)
    
    strength_score = len(strong_trumps) * 2 + total_trumps
    
    print(f"  Trump analysis: {total_trumps} trumps, {len(strong_trumps)} strong (1,R,D,V,10)")
    print(f"  Trump strength score: {strength_score}")
    
    return strength_score


def should_ask_to_play(hand, trump_suit, player_name):
    """Determine if a player should ask to play based on their cards"""
    trump_strength = evaluate_trump_strength(hand, trump_suit)
    
    # Good trump hand criteria:
    # - At least 4 trump cards with 2+ strong ones (score >= 8)
    # - Or at least 6 trump cards total (score >= 6)
    should_ask = trump_strength >= 6
    
    if should_ask:
        print(f"  {player_name} has a good trump hand - should ASK")
    else:
        print(f"  {player_name} has a weak trump hand - should PASS")
    
    return should_ask


def conduct_bidding(players, trump_suit, trump_card_holder):
    """Conduct the bidding phase - players decide who wants to play"""
    print(f"\n{'🎲' * 30} BIDDING PHASE {'🎲' * 30}")
    
    # Find player order starting with player after trump card holder
    all_players = ["player1", "player2", "player3", "player4"]
    trump_index = all_players.index(trump_card_holder)
    bidding_order = all_players[trump_index + 1:] + all_players[:trump_index + 1]
    
    print(f"Bidding order (starting after trump holder): {' -> '.join(bidding_order)}")
    
    asking_players = []
    
    # Each player in order decides to ask or pass
    for i, player in enumerate(bidding_order):
        hand = players[player]
        print(f"\n{player}'s turn to bid:")
        
        should_ask = should_ask_to_play(hand, trump_suit, player)
        
        # For this simulation, players follow the recommendation
        # In a real game, this would be player input
        if should_ask:
            decision = "ASK"
            asking_players.append(player)
        else:
            decision = "PASS"
        
        print(f"  {player} decision: {decision}")
        
        if decision == "ASK" and len(asking_players) == 2:
            print(f"  Two players asking - team play confirmed!")
            break
    
    return asking_players


def decide_game_mode(asking_players, players, trump_suit):
    """Decide what type of game will be played based on bidding results"""
    
    if len(asking_players) == 0:
        print(f"\n🔄 No players want to play - REDEAL!")
        return "REDEAL", [], []
    
    elif len(asking_players) == 1:
        solo_player = asking_players[0]
        
        # Check if solo player wants to play alone
        trump_strength = evaluate_trump_strength(players[solo_player], trump_suit)
        wants_solo = trump_strength >= 10  # High threshold for solo play
        
        print(f"\n🤔 {solo_player} is considering solo play...")
        print(f"  Trump strength: {trump_strength} (needs 10+ for solo)")
        
        if wants_solo:
            print(f"  {solo_player} chooses SOLO PLAY! 🎯")
            all_players = ["player1", "player2", "player3", "player4"]
            opponents = [p for p in all_players if p != solo_player]
            return "SOLO", [solo_player], opponents
        else:
            print(f"  {solo_player} declines solo play - REDEAL!")
            return "REDEAL", [], []
    
    elif len(asking_players) == 2:
        print(f"\n🤝 TEAM PLAY: {asking_players[0]} & {asking_players[1]} vs others")
        all_players = ["player1", "player2", "player3", "player4"]
        opponents = [p for p in all_players if p not in asking_players]
        return "TEAM", asking_players, opponents
    
    else:
        # More than 2 players asking - should not happen with proper bidding
        print(f"\n⚠️  Too many players asking - REDEAL!")
        return "REDEAL", [], []


def reassemble_and_redeal_deck(players):
    """Collect all cards, reassemble deck and redeal"""
    print(f"\n♻️  REASSEMBLING DECK FOR REDEAL...")
    
    # Collect all cards from all players
    all_cards = []
    for player, hand in players.items():
        all_cards.extend(hand)
        players[player] = []  # Clear player hands
    
    # Shuffle the collected cards
    random.shuffle(all_cards)
    
    # Cut the deck
    all_cards = cut_deck(all_cards)
    
    print(f"  Collected {len(all_cards)} cards, shuffled and cut")
    return all_cards


def calculate_round_points(rounds_won, game_mode, playing_team, opponents):
    """Calculate points based on game mode and results with bonus points"""
    points = {"player1": 0, "player2": 0, "player3": 0, "player4": 0}
    
    if game_mode == "TEAM":
        # Team play: need 8+ rounds to win (changed from 7 to 8)
        team_wins = sum(rounds_won[player] for player in playing_team)
        
        if team_wins >= 8:
            # Base points: 2 each for winning
            base_points = 2
            # Bonus points: +1 for each round over 8
            bonus_points = team_wins - 8
            total_team_points = base_points + bonus_points
            
            print(f"🎉 Team {playing_team} wins with {team_wins}/13 rounds!")
            print(f"  Base points: {base_points}, Bonus points: {bonus_points} (for {team_wins-8} extra rounds)")
            print(f"  Total per team member: +{total_team_points} points")
            
            for player in playing_team:
                points[player] = total_team_points
            for player in opponents:
                points[player] = -total_team_points
        else:
            # Team loses - each loses 2 points, opponents get 2 each
            print(f"💀 Team {playing_team} loses with only {team_wins}/13 rounds!")
            for player in playing_team:
                points[player] = -2
            for player in opponents:
                points[player] = 2
                
    elif game_mode == "SOLO":
        # Solo play: need 5+ rounds to win
        solo_player = playing_team[0]
        solo_wins = rounds_won[solo_player]
        
        if solo_wins >= 5:
            # Base points: 6 for winning
            base_points = 6
            # Bonus calculation: for each round over 5, solo gets +3 from each opponent
            extra_rounds = solo_wins - 5
            bonus_from_each_opponent = extra_rounds * 3  # 3 points per extra round
            total_bonus = bonus_from_each_opponent  # Solo gets 3 per extra round (from all 3 opponents combined)
            total_solo_points = base_points + total_bonus
            
            print(f"🎉 Solo player {solo_player} wins with {solo_wins}/13 rounds!")
            print(f"  Base points: {base_points}")
            if extra_rounds > 0:
                print(f"  Bonus: {extra_rounds} extra rounds × 3 points = +{total_bonus} points")
            print(f"  Total solo points: +{total_solo_points}")
            
            points[solo_player] = total_solo_points
            # Each opponent loses base 2 + bonus for extra rounds
            opponent_loss = 2 + extra_rounds
            for player in opponents:
                points[player] = -opponent_loss
                
            if extra_rounds > 0:
                print(f"  Each opponent loses: -{opponent_loss} points (2 base + {extra_rounds} for extra rounds)")
        else:
            print(f"💀 Solo player {solo_player} loses with only {solo_wins}/13 rounds!")
            points[solo_player] = -6
            for player in opponents:
                points[player] = 2
    
    return points


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


def get_current_winning_card(dealt_cards, leading_suit, trump_suit):
    """Get the currently winning card from the dealt cards"""
    # First check for trump cards
    trump_cards = [card for card in dealt_cards if card['suit'] == trump_suit and card['suit'] != leading_suit]
    if trump_cards:
        return best_card(trump_cards)
    
    # If no trump cards, look for leading suit cards
    leading_suit_cards = [card for card in dealt_cards if card['suit'] == leading_suit]
    if not leading_suit_cards:
        return None
    return best_card(leading_suit_cards)


def can_beat_current_winner(card, current_winner, trump_suit, leading_suit):
    """Check if a card can beat the current winning card"""
    if current_winner is None:
        return True
    
    # If current winner is trump and our card is not trump, we can't beat it
    if current_winner['suit'] == trump_suit and card['suit'] != trump_suit:
        return False
    
    # If our card is trump and current winner is not trump, we beat it
    if card['suit'] == trump_suit and current_winner['suit'] != trump_suit:
        return True
    
    # Both are trump or both are not trump - compare ranks
    if card['suit'] == current_winner['suit']:
        return get_rank_value(card['rank']) < get_rank_value(current_winner['rank'])
    
    # Different suits, neither trump - can't beat
    return False


def get_round_winner(dealt_cards, player_order, leading_suit, trump_suit):
    """Determine the winner of the round based on highest card, considering trump"""
    best_card_index = -1
    best_card = None
    
    for i, (player, card) in enumerate(zip(player_order, dealt_cards)):
        if best_card is None:
            best_card = card
            best_card_index = i
        elif can_beat_current_winner(card, best_card, trump_suit, leading_suit):
            best_card = card
            best_card_index = i
    
    return player_order[best_card_index]


def rotate_player_order(player_names, starting_player):
    """Rotate player order so starting_player starts"""
    start_index = player_names.index(starting_player)
    return player_names[start_index:] + player_names[:start_index]


def play_game_round(cards, game_round_number, starting_player):
    """Play one complete game round (13 turns) with bidding system"""
    
    # Keep trying until we get a valid game (no redeal)
    while True:
        print(f"\n{'#' * 60}")
        print(f"# GAME ROUND {game_round_number}")
        print(f"# Starting player: {starting_player}")
        print(f"{'#' * 60}")

        # Determine trump suit from last card (but don't remove it yet)
        trump_suit = determine_trump_suit(cards)

        players = {"player1": [], "player2": [], "player3": [], "player4": []}
        player_names = list(players.keys())
        
        # Deal ALL 52 cards using the normal 4-4-5 distribution
        # Each player gets exactly 13 cards
        players = deal_deck(cards, players)
        
        # Find which player got the trump card
        trump_card = cards[-1]  # The last card that determined trump suit
        trump_card_holder = None
        for player, hand in players.items():
            for card in hand:
                if card['rank'] == trump_card['rank'] and card['suit'] == trump_card['suit']:
                    trump_card_holder = player
                    break
            if trump_card_holder:
                break
        
        print(f"\n🎯 Trump card ({trump_card['rank']} of {trump_card['suit']}) is with: {trump_card_holder}")
        
        print("\nInitial hands:")
        for player, hand in players.items():
            print(f"{player}: {len(hand)} cards")

        # BIDDING PHASE
        asking_players = conduct_bidding(players, trump_suit, trump_card_holder)
        game_mode, playing_team, opponents = decide_game_mode(asking_players, players, trump_suit)
        
        # Handle redeal
        if game_mode == "REDEAL":
            print(f"  🔄 REDEAL: Collecting all cards and reshuffling...")
            
            # Collect all 52 cards from all players (4 stacks of 13 cards each)
            all_cards = []
            for player, hand in players.items():
                print(f"    Collecting {len(hand)} cards from {player}")
                all_cards.extend(hand)
                players[player] = []  # Clear player hands
            
            # Shuffle and prepare for redeal
            random.shuffle(all_cards)
            cards = cut_deck(all_cards)
            print(f"  Redeal complete: {len(all_cards)} cards reshuffled (4 stacks of 13)")
            continue  # Restart the round
        
        # If we get here, we have a valid game mode
        break  # Exit the while loop

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
            
            # Safety check - if player has no cards, skip
            if not player_hand:
                print(f"{player}: No cards left!")
                continue

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
                    current_winner = get_current_winning_card(dealt_cards, leading_suit, trump_suit)
                    best_in_suit = best_card(cards_in_suit)

                    if can_beat_current_winner(best_in_suit, current_winner, trump_suit, leading_suit):
                        # Can win - play best card in suit
                        card_to_play = best_in_suit
                        print(f"{player} can beat current winner, playing best card in suit")
                    else:
                        # Can't win - play worst card in suit to save better cards
                        card_to_play = worst_card(cards_in_suit)
                        print(f"{player} can't beat current winner, playing worst card in suit")
                else:
                    # No cards in leading suit - can play trump or any card
                    trump_cards = filter_cards_by_suit(player_hand, trump_suit)
                    current_winner = get_current_winning_card(dealt_cards, leading_suit, trump_suit)
                    
                    if trump_cards and (current_winner is None or current_winner['suit'] != trump_suit):
                        # Has trump and current winner is not trump - play best trump
                        card_to_play = best_card(trump_cards)
                        print(f"{player} has no cards in leading suit, playing trump card to win")
                    elif trump_cards and current_winner['suit'] == trump_suit:
                        # Current winner is trump - check if we can beat it
                        best_trump = best_card(trump_cards)
                        if can_beat_current_winner(best_trump, current_winner, trump_suit, leading_suit):
                            card_to_play = best_trump
                            print(f"{player} playing better trump card to win")
                        else:
                            # Can't beat trump - play worst card overall
                            card_to_play = worst_card(player_hand)
                            print(f"{player} can't beat trump, playing worst card overall")
                    else:
                        # No trump cards or can't use them - play worst card overall
                        card_to_play = worst_card(player_hand)
                        print(f"{player} has no cards in leading suit and no useful trump, playing worst card overall")

            trump_indicator = " 🎯" if card_to_play['suit'] == trump_suit else ""
            print(f"{player}: {card_to_play}{trump_indicator}")
            players[player].remove(card_to_play)
            dealt_cards.append(card_to_play)

        # Determine winner
        winner = get_round_winner(dealt_cards, player_names, leading_suit, trump_suit)
        rounds_won[winner] += 1

        # Winner collects all 4 cards in random order
        random.shuffle(dealt_cards)
        collected_cards[winner].extend(dealt_cards)

        print(f"\n🏆 {winner} wins this turn and collects 4 cards!")

        # Rotate player order for next turn
        player_names = rotate_player_order(all_players, winner)

    # Calculate final points based on game mode
    print(f"\n{'=' * 60}")
    print(f"GAME ROUND {game_round_number} COMPLETE!")
    print(f"Rounds won: {rounds_won}")
    print(f"Game mode: {game_mode}")
    if game_mode in ["TEAM", "SOLO"]:
        print(f"Playing team: {playing_team}")
        print(f"Opponents: {opponents}")
    
    round_points = calculate_round_points(rounds_won, game_mode, playing_team, opponents)
    
    print(f"\nPoints awarded:")
    for player, pts in round_points.items():
        if pts != 0:
            print(f"{player}: {pts:+d} points")
    
    for player in collected_cards:
        print(f"{player}: {len(collected_cards[player])} cards")

    return round_points, collected_cards


def reassemble_deck(collected_cards):
    """Reassemble deck from collected cards - stacks stay together but order is randomized"""
    player_names = list(collected_cards.keys())
    # Each player's collected cards are divided into stacks of 4
    all_stacks = []
    for player in player_names:
        cards = collected_cards[player]
        all_stacks.append(cards)

    # Randomly shuffle the order of stacks
    random.shuffle(all_stacks)
    # Flatten the stacks back into a single deck
    reassembled = []
    for stack in all_stacks:
        reassembled.extend(stack)

    # Cut the deck (no shuffling)
    reassembled = cut_deck(reassembled)

    return reassembled


def game():
    """Main game function - plays multiple rounds until someone reaches 15 points"""
    # Initialize deck for first round
    cards = initial_deck()

    total_points = {"player1": 0, "player2": 0, "player3": 0, "player4": 0}

    # Starting player rotates each game round
    all_players = ["player1", "player2", "player3", "player4"]
    game_round = 1

    # Play until someone reaches 15 points
    while max(total_points.values()) < 9:
        print(f"\n{'🎯' * 20} GAME STATUS {'🎯' * 20}")
        print(f"Current scores: {total_points}")
        print(f"Target: 15 points")
        
        # Determine starting player (rotates: player1, player2, player3, player4, player1, ...)
        starting_player = all_players[(game_round - 1) % 4]

        round_points, collected_cards = play_game_round(cards, game_round, starting_player)

        # Add points to total
        for player, points in round_points.items():
            total_points[player] += points

        # Reassemble deck for next round
        cards = reassemble_deck(collected_cards)
        game_round += 1

    # Final summary
    print(f"\n{'#' * 60}")
    print("# FINAL SUMMARY")
    print(f"{'#' * 60}")
    print(f"\nFinal scores after {game_round - 1} rounds:")
    for player, points in sorted(total_points.items(), key=lambda x: x[1], reverse=True):
        print(f"{player}: {points} points")

    winner = max(total_points, key=total_points.get)
    print(f"\n🎉 OVERALL WINNER: {winner} with {total_points[winner]} points! 🎉")


if __name__ == "__main__":
    game()