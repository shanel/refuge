import abc
import random


class BaseUser(metaclass=abc.ABCMeta):
    """Represents the data necessary for a user to participate in lotteries."""
    @abc.abstractmethod
    def percentage(self):
        pass

    @abc.abstractmethod
    def enter_lottery(self):
        pass

    @abc.abstractmethod
    def exit_lottery(self):
        pass

    @abc.abstractmethod
    def win_lottery(self):
        pass

    @abc.abstractmethod
    def get_rank(self):
        pass


def run_a_single_lottery_draw(users, ticket_holders):
    # Get pass entries for each holder
    holder_passes = {}
    for holder in ticket_holders:
        holder_passes[holder] = users[holder].get_rank()

    # Sorted list of holders ordered by pass count
    sorted_holders = sorted(holder_passes.items(), key=lambda kv: kv[1])

    return sorted_holders[0][0]


def run_a_lottery_with_random_users(users,
                                    holder_count,
                                    slots,
                                    but_not=None,
                                    final=None):
    winners = []
    viable = users.keys()
    if but_not != None:
        viable = set(viable) - set(but_not)
    holders = random.sample(viable, holder_count)
    original_holders = holders
    for h in holders:
        users[h].enter_lottery()
    for i in range(slots):
        winner = run_a_single_lottery_draw(users, holders)
        holders.remove(winner)
        winners += winner
    for winner in winners:
        users[winner].win_lottery()
    for h in original_holders:
        users[h].exit_lottery()
    if final != None:
        final()
    return winners
