import lottery


class PercentageUser(lottery.BaseUser):
    def __init__(self, name):
        self.name = name
        self.attempts = 0.0
        self.wins = 0.0

    def percentage(self):
        if self.attempts == 0:
            return 0
        return self.wins / self.attempts

    def enter_lottery(self):
        self.attempts += 1.0

    def exit_lottery(self):
        pass

    def win_lottery(self):
        self.wins += 1.0

    def get_rank(self):
        return self.percentage()
