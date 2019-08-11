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
    holder_ratings = {}
    for holder in ticket_holders:
        holder_ratings[holder] = users[holder].get_rank()

    # Sorted list of holders ordered by pass count
    sorted_holders = sorted(holder_ratings.items(),
                            key=lambda kv: (kv[1], kv[0]))
    to_return = []
    check_for = sorted_holders[0][1]
    for h in sorted_holders:
        if check_for == h[1]:
            to_return.append(h)
    if len(to_return) == 1:
        return to_return[0][0]
    else:
        return random.choice(to_return)[0]


def run_a_lottery_with_random_users(lottery,
                                    users,
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
        users[h].enter_lottery(lottery)
    for i in range(slots):
        winner = run_a_single_lottery_draw(users, holders)
        holders.remove(winner)
        winners += winner
    for winner in winners:
        users[winner].win_lottery(lottery)
    for h in original_holders:
        users[h].exit_lottery()
    if final != None:
        final()
    return winners
