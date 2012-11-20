from deck import Deck
from dealer import Dealer

dealer = Dealer()
deck = Deck(6)

N_HANDS = 1000000
dealer_busts = 0

for i in range(0,N_HANDS):
    deck.shuffle()
    dealer.reset_hand()
    dealer.add_card(deck.draw())
    dealer.add_card(deck.draw())
    dealer.play_hand(deck)

    if dealer.is_busted():
        dealer_busts += 1

print float(dealer_busts) / N_HANDS
