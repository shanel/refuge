import random
import lottery

import percentage
import stride


def do_nothing():
    pass


def main():
    lottery_number = 0
    types = {
        "stride": stride.StrideUser,
        "percentage": percentage.PercentageUser
    }
    finals = {"stride": stride.update_global_pass, "percentage": do_nothing}

    # Create alphabet list of uppercase letters
    alphabet = []
    for letter in range(65, 91):
        alphabet.append(chr(letter))

    chunks = [alphabet[:10]]
    sub_alphabet = alphabet[10:]

    while len(sub_alphabet) > 0:
        chunk = []
        for _ in range(random.randint(1, 5)):
            if len(sub_alphabet) > 0:
                chunk.append(sub_alphabet.pop(0))
        chunks.append(chunk)

    repeat = False

    abstensions = []

    for kind, user_type in types.items():
        print(kind)
        users = {}
        abs_copy = abstensions[:]

        for chunk in chunks:
            for a in chunk:
                users[a] = user_type(a)
            for _ in range(5):
                if not repeat:
                    ab = random.sample(users.keys(), 3)
                    abstensions.append(ab)
                else:
                    ab = abs_copy.pop(0)
                lottery.run_a_lottery_with_random_users(lottery_number,
                                                        users,
                                                        7,
                                                        4,
                                                        ab,
                                                        final=finals[kind])
                lottery_number += 1

        total = 0
        for k, v in users.items():
            total += v.percentage() * 100
            print("%s: %d (%d / %d)" %
                  (k, v.percentage() * 100, len(v.wins), len(v.attempts)))

        print(kind)
        avg = total / len(users.keys())

        dev_total = 0
        for k, v in users.items():
            dev_total += abs(avg - (v.percentage() * 100))

        print(avg)
        print(dev_total / len(users.keys()))
        repeat = True


if __name__ == "__main__":
    main()
