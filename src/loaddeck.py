import json
import random

# Read JSON from a file
with open('deck.json', 'r') as file:
    data = json.load(file)

# Access the cards
cards = data['cards']
print(cards[0])  # First card: {'rank': '1', 'suit': 'Klaveren'}
print(cards)

random.shuffle(cards)

print(cards[0])
print(cards)

cut_point = random.randint(1, len(cards) - 1)
cards = cards[cut_point:] + cards[:cut_point]

print(cards[0])
print(cards)
