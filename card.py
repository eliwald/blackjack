class Card(object):
    number = -1
    suit = -1

    def __init__(self, n, s):
        self.number = n
        self.suit = s

    def value(self):
        if self.number == 1:
            return 11
        if self.number >= 11:
            return 10
        return self.number

    def hard_value(self):
        if self.number == 1:
            return 1
        return self.value()

    def suit(self):
        return self.suit

    def __str__(self):
        if self.suit == 0:
            s = "Clubs"
        elif self.suit == 1:
            s = "Diamonds"
        elif self.suit == 2:
            s = "Hearts"
        else:
            s = "Spades"
        if self.number == 1:
            ns = "A"
        elif self.number == 11:
            ns = "J"
        elif self.number == 12:
            ns = "Q"
        elif self.number == 13:
            ns = "K"
        else:
            ns = str(self.number)
        return "%s of %s" % (ns, s)
