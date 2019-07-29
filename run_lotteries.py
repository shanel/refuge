import random
import lottery

import percentage
import stride


def do_nothing():
    pass


def main():
    types = {
        "stride": stride.StrideUser,
        "percentage": percentage.PercentageUser
    }
    finals = {"stride": stride.update_global_pass, "percentage": do_nothing}
    for kind, user_type in types.items():
        print(kind)
        users = {}

        # Create alphabet list of uppercase letters
        alphabet = []
        for letter in range(65, 91):
            alphabet.append(chr(letter))

        for _ in range(10):
            i = alphabet.pop(0)
            users[i] = user_type(i)

        while len(alphabet) > 0:
            for _ in range(random.randint(1, 5)):
                if len(alphabet) > 0:
                    i = alphabet.pop()
                    users[i] = user_type(i)
            for _ in range(5):
                lottery.run_a_lottery_with_random_users(users,
                                                        7,
                                                        4,
                                                        random.sample(
                                                            users.keys(), 4),
                                                        final=finals[kind])

        total = 0
        for k, v in users.items():
            total += v.percentage() * 100
            print("%s: %d (%d / %d)" %
                  (k, v.percentage() * 100, v.wins, v.attempts))

        print(kind)
        avg = total / len(users.keys())

        dev_total = 0
        for k, v in users.items():
            dev_total += abs(avg - (v.percentage() * 100))

        print(avg)
        print(dev_total / len(users.keys()))


if __name__ == "__main__":
    main()
