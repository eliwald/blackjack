from card import Card
from hand import Hand
from deck import Deck
from dealer import Dealer

import sys
from time import time
from pickle import Pickler, Unpickler, PickleError

N_HANDS = 10000
N_DECKS = 6
STAY_OUTCOMES_FILE = "./stay_outcomes_%s.txt" % (N_HANDS)
DOUBLE_OUTCOMES_FILE = "./double_outcomes_%s.txt" % (N_HANDS)

KEEP_TIMING = 0

def create_stay_outcomes(desired_iterations):
    try:
        stay_outcomes = unpickle_outcomes(STAY_OUTCOMES_FILE, desired_iterations)
        print "Found pickled run of stay outcomes - returning..."
        return stay_outcomes
    except IOError:
        print "Couldn't find pickled stay_outcomes - creating them..."
    except PickleError:
        print "Pickle error - continuing..."

    stay_outcomes = {"ITERATIONS" : desired_iterations}
    if KEEP_TIMING:
        time_map = {"deck shuffling" : 0,
                    "dealer playing": 0,
                    "hand comparison": 0}
    d = Deck(N_DECKS)
    dealer = Dealer()

    for hand_val in range(3, 22):
        print "HAND VALUE %d" % hand_val
        stay_outcomes[hand_val] = {}
        for dealer_upcard in range(1,11):
            stay_outcomes[hand_val][dealer_upcard] = [0, 0]

        for i in range(0, desired_iterations):
            if not i % 10000:
                print "Iteration %d..." % i
            has_blackjack = True
            while has_blackjack:
                if KEEP_TIMING:
                    start_t = time()
                d.library_shuffle()
                if KEEP_TIMING:
                    end_t = time()
                    time_map["deck shuffling"] += end_t - start_t
                    start_t = time()
            
                dealer.reset_hand()
                c1 = d.draw()
                dealer_upcard = c1
                dealer.add_card(c1)
                dealer.add_card(d.draw())
                has_blackjack = dealer.has_blackjack()

            dealer.play_hand(d)
            if KEEP_TIMING:
                end_t = time()
                time_map["dealer playing"] += end_t - start_t
                start_t = time()

            dealer_val = dealer.value()
            if dealer_val < hand_val or dealer.is_busted():
                stay_outcomes[hand_val][c1.hard_value()][0] += 1
            elif dealer_val == hand_val:
                stay_outcomes[hand_val][c1.hard_value()][0] += .5
            stay_outcomes[hand_val][c1.hard_value()][1] += 1
            if KEEP_TIMING:
                end_t = time()
                time_map["hand comparison"] += end_t - start_t
                start_t = time()

    pickle_outcomes(stay_outcomes, STAY_OUTCOMES_FILE)
    return stay_outcomes

def create_double_outcomes(desired_iterations):
    try:
        double_outcomes = unpickle_outcomes(DOUBLE_OUTCOMES_FILE, desired_iterations)
        print "Found pickled run of double outcomes - returning..."
        return double_outcomes
    except IOError:
        print "Couldn't find pickled double_outcomes - creating them..."
    except PickleError:
        print "Pickle error - continuing..."

    stay_outcomes = create_stay_outcomes(desired_iterations)
    double_outcomes = {"ITERATIONS" : desired_iterations}
    for v in stay_outcomes:
        if v == "ITERATIONS" or v == 21:
            continue
        double_outcomes[v] = {}
        for upc in stay_outcomes[v]:
            double_outcomes[v][upc] = [0, 0]

            # 2-10
            for i in range(2, 11):
                if v + i <= 21:
                    stay_percent = (float(stay_outcomes[v + i][upc][0]) / float(stay_outcomes[v + i][upc][1]))
                    double_outcomes[v][upc][0] += 4 * stay_percent if i == 10 else stay_percent

            # Aces
            if v + 11 <= 21:
                card_val = 11
            else:
                card_val = 1
            double_outcomes[v][upc][0] += float(stay_outcomes[v + card_val][upc][0]) / float(stay_outcomes[v + card_val][upc][1])

            double_outcomes[v][upc][1] = 13

    pickle_outcomes(double_outcomes, DOUBLE_OUTCOMES_FILE)
    return double_outcomes

def main():
    stay_outcomes = create_stay_outcomes(N_HANDS)
    double_outcomes = create_double_outcomes(N_HANDS)
    print "\n*** STAY OUTCOMES ***"
    prettyprint_outcomes(stay_outcomes)
    print "\n*** DOUBLE OUTCOMES ***"
    prettyprint_outcomes(double_outcomes)

def prettyprint_outcomes(outcomes):
    percents = {}
    for v in outcomes:
        if v == "ITERATIONS":
            continue
        percents[v] = {}
        for upc in outcomes[v]:
            try:
                percents[v][upc] = float(outcomes[v][upc][0]) / float(outcomes[v][upc][1])
            except ZeroDivisionError:
                percents[v][upc] = -1.0

    for v in percents:
        print "%d" % v
        for upc in percents[v]:
            print "\t%d: %.3f" % (upc, percents[v][upc])

            if KEEP_TIMING:
                end_t = time()
                time_map["float conversion"] = end_t - start_t
                sys.stdout.write(str(time_map) + "\n")

def pickle_outcomes(outcomes, fn):
    fh = open(fn, 'w')
    p = Pickler(fh)
    p.dump(outcomes)
    fh.close()
    if KEEP_TIMING:
        end_t = time()
        time_map["pickling"] = end_t - start_t
        start_t = time()

def unpickle_outcomes(fn, desired_iterations):
        fh = open(fn, 'r')
        unp = Unpickler(fh)
        outcomes = unp.load()
        fh.close()
        kept_iterations = outcomes["ITERATIONS"]
        if kept_iterations == desired_iterations:
            return outcomes
        raise IOError

if __name__ == "__main__":
    main()
