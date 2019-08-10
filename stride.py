#!/usr/bin/env python3

import lottery

STARTING_TICKETS = 10.0
STRIDE1 = (1 << 20)  # This is the big number to divide
QUANTUM = (1 << 20)

global_tickets = 0.0
global_stride = 0.0
global_pass = 0.0  # should be incremented after each full lottery


def update_global_tickets(count):
    global global_tickets
    global global_stride
    global_tickets += count
    global_stride = STRIDE1 / global_tickets


def update_global_pass():
    """Only run after a lottery occurs."""
    global global_pass
    global_pass += global_stride / QUANTUM


class StrideUser(lottery.BaseUser):
    def __init__(self, name, tickets=STARTING_TICKETS):
        self.name = name
        self.tickets = tickets
        self.pass_count = global_pass
        self.remain = self.stride()
        self.attempts = []
        self.wins = []

    def stride(self):
        return STRIDE1 / self.tickets

    def percentage(self):
        if len(self.attempts) == 0:
            return 0
        return float(len(self.wins)) / float(len(self.attempts))

    def enter_lottery(self, lottery):
        self.pass_count = global_pass + self.remain
        self.attempts.append(lottery)
        update_global_tickets(self.tickets)

    def exit_lottery(self):
        self.remain = self.pass_count - global_pass
        update_global_tickets(-1.0 * self.tickets)

    def win_lottery(self, lottery):
        self.wins.append(lottery)
        self.pass_count = self.stride() / QUANTUM

    def get_rank(self):
        return self.pass_count
