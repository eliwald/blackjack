import card

class Hand(object):
    cl = []
    
    def __init__(self, cards = []):
        self.cl = cards

    def hard_value(self):
        val = 0
        for c in self.cl:
            val += c.hard_value()
        return val
        
    def soft_value(self):
        val = 0
        seen_ace = False
        for c in self.cl:
            if not seen_ace:
                val += c.value()
                if c.value() == 11:
                    seen_ace = True
            else:
                val += c.hard_value()                
        return val

    def contains_ace(self):
        for c in self.cl:
            if c.value() == 11:
                return True
        return False

    def is_soft(self):
        return (self.soft_value() <= 21 and self.contains_ace())

    def can_split(self):
        return (len(self.cl) == 2 and self.cl[0] == self.cl[1])

    def can_double(self):
        return (len(self.cl) == 2)

    def value(self):
        v = self.soft_value()
        if v <= 21:
            return v
        return self.hard_value()

    def is_busted(self):
        return (self.value() > 21)

    def is_blackjack(self):
        return len(self.cl) == 2 and self.value() == 21

    def add_card(self, c):
        self.cl.append(c)

    def clear(self):
        self.cl = []

    def __str__(self):
        return str([str(c) for c in self.cl])
