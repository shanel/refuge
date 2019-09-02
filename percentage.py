import json
import lottery


class PercentageUser(lottery.BaseUser):
    def __init__(self, name):
        self.name = name
        self.attempts = []
        self.wins = []

    def percentage(self):
        if self.attempts:
            return float(len(self.wins)) / float(len(self.attempts))
        return 0

    def enter_lottery(self, lottery_id):
        self.attempts.append(lottery_id)

    def exit_lottery(self):
        pass

    def win_lottery(self, lottery_id):
        self.wins.append(lottery_id)

    def get_rank(self):
        return self.percentage()


class PlayerMixIn():
    def enter_lottery(self, lottery_id):
        lotteries_participated_in = []
        if self.lotteries_participated_in:
            lotteries_participated_in = json.loads(
                self.lotteries_participated_in)
        lotteries_participated_in.append(lottery_id)
        self.lotteries_participated_in = json.dumps(lotteries_participated_in)
        # Assuming we only need to do the put at the end of the lottery?
        # self.put()

    def win_lottery(self, lottery_id):
        lotteries_won = []
        if self.lotteries_won:
            lotteries_won = json.loads(self.lotteries_won)
        lotteries_won.append(lottery_id)
        self.lotteries_won = json.dumps(lotteries_won)

    def exit_lottery(self):
        self.put()

    def get_rank(self):
        lotteries_participated_in = []
        if self.lotteries_participated_in:
            lotteries_participated_in = json.loads(
                self.lotteries_participated_in)
        if not lotteries_participated_in:
            return 0.0
        lotteries_won = []
        if self.lotteries_won:
            lotteries_won = json.loads(self.lotteries_won)
        return float(len(lotteries_won)) / float(
            len(lotteries_participated_in))
