import argparse
import random

import math
from qiskit import IBMQ, QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.tools.monitor import job_monitor

import executor

IBMQ.providers()

SHOTS = 1024
run_on_real = False


def comp_move():
    return random.randint(0, 5)  # Computer's moves are dumb. But that doesn't matter for this exercise


def print_status(status, ship_pos):  # Clean this method up
    status_for_pos = status_at_pos(ship_pos, status)
    print_layout(status_for_pos)


def status_at_pos(ship_pos, status):
    status_for_pos = []
    for pos in range(5):
        if pos in ship_pos:
            idx = ship_pos.index(pos)
            damage_to_ship = status[idx]
            if damage_to_ship - 0 < 5:
                status_for_pos.append('?')
            else:
                status_for_pos.append('%d%%' % status[idx])
        else:
            status_for_pos.append('?')
    return status_for_pos


def print_layout(lst):
    print('%s       %s' % (lst[4], lst[0]))
    print('|\\     /|')
    print('| \\   / |')
    print('|  \\ /  |')
    print('|   %s   |' % lst[2])
    print('|  / \\  |')
    print('| /   \\ |')
    print('|/     \\|')
    print('%s       %s' % (lst[3], lst[1]))


def main():
    parser = argparse.ArgumentParser(description='Run on real quantum computer')
    parser.add_argument('-r', '--real', dest='real', default=False, action='store_true',
                        help='Run on real quantum computer')  # Extract to separate reusable component
    global run_on_real
    run_on_real = parser.parse_args().real
    ship_pos = [get_ship_pos(), create_ship_pos()]
    bombs = [[0, 0, 0], [0, 0, 0]]
    status = [[0, 0, 0], [0, 0, 0]]
    while not game_over(status):
        bomb_pos_0 = int(input("Where do you want to bombs? "))
        add_bomb(ship_pos[1], bombs[0], bomb_pos_0, status[1])
        add_bomb(ship_pos[0], bombs[1], comp_move(), status[0])
        status = calc_result(bombs)

        print("Damage to your ships:")
        print_status(status[0], ship_pos[0])
        print("Damage to computer's ships:")
        print_status(status[1], ship_pos[1])

    print("Game over!")


def prompt_for_bomb():
    while True:
        bomb_pos = int(input("Where do you want to bombs? "))
        if bomb_pos in range(5):
            return bomb_pos


def add_bomb(ship_pos, bombs, bomb_pos, status):
    if bomb_pos in ship_pos:
        bombed_ship = ship_pos.index(bomb_pos)
        if status[bombed_ship] < 100:
            bombs[bombed_ship] += 1


def game_over(status):
    ships_destroyed_p1 = len([x for x in status[0] if x == 100])
    ships_destroyed_p2 = len([x for x in status[1] if x == 100])
    return ships_destroyed_p1 == 3 or ships_destroyed_p2 == 3


def get_ship_pos():
    print_layout(['0', '1', '2', '3', '4'])
    prompt = "Enter the position of yours ships. Should be 3 uniq integers between 0 & 4. "

    while True:
        input_pos = [int(x) for x in input(prompt).split()]
        if valid_pos(input_pos):
            return input_pos


def valid_pos(input_pos):
    used = set()
    if len(input_pos) != 3:
        return False
    for i in input_pos:
        if i > 4 or i < 0:
            return False  # should be within 0-4
        if i in used:
            return False  # check uniqueness
        used.add(i)
    return True


def create_ship_pos():
    list_of_pos = [x for x in range(5)]
    random.shuffle(list_of_pos)
    return list_of_pos[:3]


def calc_result(bombs):
    qc = make_circuit(bombs)
    job = executor.execute(qc, SHOTS, run_on_real)
    job_monitor(job)
    results = job.result().get_counts()
    damage = meas_to_damage(results)
    status = [damage[1], damage[0]]  # Flip the order of damage caused to show status of ships
    return status


def make_circuit(bombs):
    qc = []

    for player in range(2):
        q = QuantumRegister(3)
        c = ClassicalRegister(3)
        qc.append(QuantumCircuit(q, c))
        for pos_idx in range(3):
            bomb_count = bombs[player][pos_idx]
            for _ in range(bomb_count):
                qc[player].u3(math.pi / (pos_idx + 1), 0.0, 0.0, q[pos_idx])
        for qubit in range(3):
            qc[player].measure(q[qubit], c[qubit])

    return qc[0] + qc[1]  # is there a better way to combine two circuits into one program?


def hits_to_damage(hits):
    if hits < 0.2 * SHOTS:
        return 0
    if hits > 0.9 * SHOTS:
        return 100
    else:
        return hits * 100 / SHOTS


def meas_to_damage(counts):
    hits_list = [[0, 0, 0], [0, 0, 0]]
    for state, hits in counts.items():
        state = state[::-1]  # reverse order
        state0 = state[:3]
        state1 = state[4:]
        for i in range(3):
            if state0[i] == '1':
                hits_list[0][i] += hits
            if state1[i] == '1':
                hits_list[1][i] += hits
    damage = [[hits_to_damage(x) for x in player_list] for player_list in hits_list]
    return damage


if __name__ == "__main__":
    main()
