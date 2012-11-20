from card import Card
from hand import Hand
from deck import Deck

class Dealer(object):
    h = Hand()

    def __init__(self, my_hand = Hand()):
        self.h = my_hand

    def add_card(self, c):
        self.h.add_card(c)

    def reset_hand(self):
        self.h.clear()

    def play_hand(self, d):
        if self.h.value() > 17:
            return
        
        if self.h.value() == 17:
            if self.h.is_soft():
                self.add_card(d.draw())
                return self.play_hand(d)
            return

        self.add_card(d.draw())
        return self.play_hand(d)

    def value(self):
        return self.h.value()

    def is_busted(self):
        return self.value() > 21

    def has_blackjack(self):
        return self.h.is_blackjack()

    def __str__(self):
        return str(self.h)
