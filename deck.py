from card import Card
from hand import Hand
import random

class Deck(object):
    cl = []
    curr_card = -1

    def __init__(self, n_decks = 1):
        self.cl = Deck.new_decklist(n_decks)
        self.curr_card = 0

    @staticmethod
    def new_decklist(n_decks):
        cards = []
        for d in range(0, n_decks):
            for c in range(1, 14):
                for s in range(0, 4):
                    cards.append(Card(c, s))
        return cards

    def shuffle(self):
        n = len(self.cl)
        places = []
        for i in range(0, n):
            places.append(i)

        new_cl = []
        for i in range(0, n):
            rand = int(random.random()*(n - i))
            ind = places[rand]
            new_cl.append(self.cl[ind])
            places[rand] = places[n - i - 1]

        self.cl = new_cl
        self.curr_card = 0

    def library_shuffle(self):
        random.shuffle(self.cl)
        self.curr_card = 0

    def draw(self):
        c = self.cl[self.curr_card]
        self.curr_card += 1
        return c

    def __str__(self):
        return str([str(c) for c in self.cl])
