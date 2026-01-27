import json
import random
import os

class DeckLoader:
    def __init__(self):
        self.cards = []
        self.load_deck()

    def load_deck(self):
        # Look for deck.json in the same directory as this file
        path = os.path.join(os.path.dirname(__file__), 'deck.json')
        with open(path, 'r') as file:
            self.cards = json.load(file)['cards']

    def __shuffle_and_cut(self):
        random.shuffle(self.cards)
        cut_point = random.randint(1, len(self.cards) - 1)
        new_deck = self.cards[cut_point:] + self.cards[:cut_point]
        self.deck = new_deck

    def print_deck(self):
        for card in self.cards:
            suit = card['suit']
            rank = card['rank']

            match suit:
                case "Ruiten":
                    print("♦" + rank, sep=' ')
                case "Harten":
                    print("♥" + rank, sep=' ')
                case "Klaveren":
                    print("♣" + rank, sep=' ')
                case "Schoppen":
                    print("♠" + rank, sep=' ')
