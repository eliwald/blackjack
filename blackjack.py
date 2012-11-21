from card import Card
from hand import Hand
from deck import Deck
from dealer import Dealer

import sys
from time import time
from pickle import Pickler, Unpickler, PickleError

DEFAULT_N_HANDS = 10000
if len(sys.argv) > 1:
    try:
        N_HANDS = int(sys.argv[1])
    except ValueError:
        print "First argument must be an int (number of hands to try per case). Defaulting to %d." % (DEFAULT_N_HANDS)
        N_HANDS = DEFAULT_N_HANDS
else:
    N_HANDS = DEFAULT_N_HANDS

N_DECKS = 6
STAY_OUTCOMES_FILE = "./stay_outcomes_%s.txt" % (N_HANDS)
DOUBLE_OUTCOMES_FILE = "./double_outcomes_%s.txt" % (N_HANDS)
HARD_HIT_OUTCOMES_FILE = "./hard_hit_outcomes_%s.txt" % (N_HANDS)
SOFT_HIT_OUTCOMES_FILE = "./soft_hit_outcomes_%s.txt" % (N_HANDS)
HARD_MOVES_FILE = "./hard_moves_%s.txt" % (N_HANDS)
SOFT_MOVES_FILE = "./soft_moves_%s.txt" % (N_HANDS)

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
    soft_double_outcomes = {"ITERATIONS" : desired_iterations}
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

def create_hit_and_soft_outcomes(desired_iterations):
    HARD_HIT_OUTCOMES_FOUND = False
    try:
        hard_hit_outcomes = unpickle_outcomes(HARD_HIT_OUTCOMES_FILE, desired_iterations)
        print "Found pickled run of hit outcomes..."
        HARD_HIT_OUTCOMES_FOUND = True
    except IOError:
        print "Couldn't find pickled hit outcomes - creating hit outcomes and soft outcomes..."
    except PickleError:
        print "Pickle error - continuing..."

    if HARD_HIT_OUTCOMES_FOUND:
        try:
            soft_hit_outcomes = unpickle_outcomes(SOFT_HIT_OUTCOMES_FILE, desired_iterations)
            print "...and found pickled run of soft outcomes as well - returning..."
            return (hard_hit_outcomes, soft_hit_outcomes)
        except IOError:
            print "...but couldn't find pickled soft outcomes - creating hit outcomes and soft outcomes..."
        except PickleError:
            print "Pickle error - continuing..."

    stay_outcomes = create_stay_outcomes(desired_iterations)
    double_outcomes = create_double_outcomes(desired_iterations)
    hard_hit_outcomes = {"ITERATIONS" : desired_iterations}
    soft_hit_outcomes = {"ITERATIONS" : desired_iterations}
    hard_hit_outcomes[21] = {}
    soft_hit_outcomes[21] = {}
    for upc in stay_outcomes[21]:
        hard_hit_outcomes[21][upc] = [0, 13]
        soft_hit_outcomes[21][upc] = [0, 13]

    # Hard hits to a 2-10
    for cur_val in reversed(range(3, 21)):
        hard_hit_outcomes[cur_val] = {}
        for upc in stay_outcomes[cur_val]:
            hard_hit_outcomes[cur_val][upc] = [0,0]

            #2-10
            for i in range(2,11):
                if cur_val + i <= 21:
                    stay_percent = calculate_percent(stay_outcomes, cur_val + i, upc)
                    hit_percent = calculate_percent(hard_hit_outcomes, cur_val + i, upc)
                    if i == 10:
                        percent_win = 4 * max(hit_percent, stay_percent)
                    else:
                        percent_win = max(hit_percent, stay_percent)
                    hit_outcomes[cur_val][upc][0] += percent_win

            # Missing A
            hard_hit_outcomes[cur_val][upc][1] = 12

    # Soft hits
    for cur_val in reversed(range(3,22)):
        soft_hit_outcomes[cur_val] = {}
        for upc in stay_outcomes[cur_val]:
            soft_hit_outcomes[cur_val][upc] = [0,0]

            #A-10 (second A can only be 1)
            for i in range(1,11):
                if cur_val + i <= 21:
                    new_val = cur_val + i
                    hit_percent = calculate_percent(soft_hit_outcomes, new_val, upc)
                else:
                    new_val = cur_val + i - 10
                    hit_percent = calculate_percent(hard_hit_outcomes, new_val, upc)
                stay_percent = calculate_percent(stay_outcomes, new_val, upc)

                if i == 10:
                    percent_win = 4 * max(hit_percent, stay_percent)
                else:
                    percent_win = max(hit_percent, stay_percent)
                soft_hit_outcomes[cur_val][upc][0] += percent_win

            soft_hit_outcomes[cur_val][upc][1] = 13

    # Hard hits to an A
    for cur_val in reversed(range(3, 21)):
        for upc in stay_outcomes[cur_val]:

            if cur_val + 11 <= 21:
                new_val = cur_val + 11
                hit_percent = calculate_percent(soft_hit_outcomes, new_val, upc)
            else:
                new_val = cur_val + 1
                hit_percent = calculate_percent(hard_hit_outcomes, new_val, upc)

            stay_percent = calculate_percent(stay_outcomes, new_val, upc)
            percent_win = max(hit_percent, stay_percent)
            hit_outcomes[cur_val][upc][0] += percent_win

            hit_outcomes[cur_val][upc][1] += 1

    pickle_outcomes(hard_hit_outcomes, HARD_HIT_OUTCOMES_FILE)
    pickle_outcomes(soft_hit_outcomes, SOFT_HIT_OUTCOMES_FILE)
    return (hard_hit_outcomes, soft_hit_outcomes)

def create_moves(desired_iterations):
    HARD_MOVES_FOUND = False
    try:
        hard_moves = unpickle_outcomes(HARD_MOVES_FILE, desired_iterations)
        print "Found pickled run of hard moves..."
        HARD_MOVES_FOUND = True
    except IOError:
        print "Couldn't find pickled move outcomes - creating them..."
    except PickleError:
        print "Pickle error - continuing..."

    if HARD_MOVES_FOUND:
        try:
            soft_moves = unpickle_outcomes(SOFT_MOVES_FILE, desired_iterations)
            print "...and found pickled run of soft moves as well - returning..."
            return (hard_moves, soft_moves)
        except IOError:
            print "...but couldn't find pickled soft moves - creating them..."
        except PickleError:
            print "Pickle error - continuing..."

    stay_outcomes = create_stay_outcomes(desired_iterations)
    double_outcomes = create_double_outcomes(desired_iterations)
    (hard_hit_outcomes, soft_hit_outcomes) = create_hit_and_soft_outcomes(desired_iterations)

    hard_moves = {"ITERATIONS" : desired_iterations}
    soft_moves = {"ITERATIONS" : desired_iterations}
    for v in double_outcomes:
        if v == "ITERATIONS":
            continue
        hard_moves[v] = {}
        soft_moves[v] = {}
        for upc in double_outcomes[v]:
            hard_hit_percent = calculate_percent(hard_hit_outcomes, v, upc)
            soft_hit_percent = calculate_percent(soft_hit_outcomes, v, upc)
            stay_percent = calculate_percent(stay_outcomes, v, upc)
            double_percent = calculate_percent(double_outcomes, v, upc)

            hard_hit_EV = hard_hit_percent
            soft_hit_EV = soft_hit_percent
            stay_EV = stay_percent
            double_EV = 2*double_percent - .5

            if max(hard_hit_EV, double_EV, stay_EV) < .25:
                s = "Sur"
            elif hit_EV == max(hard_hit_EV, double_EV, stay_EV):
                s = "Hit"
            elif stay_EV == max(hard_hit_EV, stay_EV, double_EV):
                s = "Stay"
            else:
                s = "Double"
            hard_moves[v][upc] = s

            if max(soft_hit_EV, double_EV, stay_EV) < .25:
                s = "Sur"
            elif soft_EV == max(soft_hit_EV, double_EV, stay_EV):
                s = "Hit"
            elif stay_EV == max(soft_hit_EV, stay_EV, double_EV):
                s = "Stay"
            else:
                s = "Double"
            soft_moves[v][upc] = s

    pickle_outcomes(hard_moves, HARD_MOVES_FILE)
    pickle_outcomes(soft_moves, SOFT_MOVES_FILE)
    return (hard_moves, soft_moves)

def main():
    stay_outcomes = create_stay_outcomes(N_HANDS)
    double_outcomes = create_double_outcomes(N_HANDS)
    (hard_hit_outcomes, soft_hit_outcomes) = create_hit_and_soft_outcomes(N_HANDS)
    (hard_moves, soft_moves) = create_moves(N_HANDS)
    print "\n*** STAY OUTCOMES ***"
    prettyprint_outcomes(stay_outcomes)
    print "\n*** DOUBLE OUTCOMES ***"
    prettyprint_outcomes(double_outcomes)
    print "\n*** HARD HIT OUTCOMES ***"
    prettyprint_outcomes(hard_hit_outcomes)
    print "\n*** SOFT HIT OUTCOMES ***"
    prettyprint_outcomes(soft_hit_outcomes)
    print "\n*** MOVE OUTCOMES ***"
    print "\n*** HARD MOVES ***"
    prettyprint_moves(hard_moves)
    print "\n*** SOFT MOVES ***"
    prettyprint_moves(soft_moves)

def calculate_percent(pair_nums, i, j):
    return (float(pair_nums[i][j][0]) / float(pair_nums[i][j][1]))

def prettyprint_moves(moves):
    sys.stdout.write("\t|")
    for i in range(1, 11):
        if not i == 10:
            sys.stdout.write("    %d   |" % i)
        else:
            sys.stdout.write("   %d   |" % i)

    sys.stdout.write("\n")
    for j in range(1, 100):
        sys.stdout.write("-")

    sys.stdout.write("\n")

    for v in moves:
        if v == "ITERATIONS":
            continue
        sys.stdout.write("%d\t|" % v)
        for upc in moves[v]:
            sys.stdout.write(" %s |" % moves[v][upc])
        sys.stdout.write("\n")
        for j in range(1, 100):
            sys.stdout.write("-")
        sys.stdout.write("\n")

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

    sys.stdout.write("\t|")
    for i in range(1, 11):
        if not i == 10:
            sys.stdout.write("    %d   |" % i)
        else:
            sys.stdout.write("   %d   |" % i)

    sys.stdout.write("\n")
    for j in range(1, 100):
        sys.stdout.write("-")

    sys.stdout.write("\n")

    for v in percents:
        sys.stdout.write("%d\t|" % v)
        for upc in percents[v]:
            if (100 * percents[v][upc] > 10):
                sys.stdout.write(" %.2f%% |" % (100 * percents[v][upc]))
            else:
                sys.stdout.write(" 0%.2f%% |" % (100 * percents[v][upc]))

            if KEEP_TIMING:
                end_t = time()
                time_map["float conversion"] = end_t - start_t
                sys.stdout.write(str(time_map) + "\n")
        sys.stdout.write("\n")
        for j in range(1, 100):
            sys.stdout.write("-")

        sys.stdout.write("\n")

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
