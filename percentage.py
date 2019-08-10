import lottery


class PercentageUser(lottery.BaseUser):
    def __init__(self, name):
        self.name = name
        self.attempts = []
        self.wins = []

    def percentage(self):
        if len(self.attempts) == 0:
            return 0
        return float(len(self.wins)) / float(len(self.attempts))

    def enter_lottery(self, lottery):
        self.attempts.append(lottery)

    def exit_lottery(self):
        pass

    def win_lottery(self, lottery):
        self.wins.append(lottery)

    def get_rank(self):
        return self.percentage()
