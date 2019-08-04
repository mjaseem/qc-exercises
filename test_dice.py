from unittest import TestCase

from qiskit.tools.monitor import job_monitor

import dice
import executor

memo = [-1]


class TestDice(TestCase):
    def test_n_tos(self):
        max_ratio = 1.0
        for i in range(1, 10000000):
            max_ratio = max(max_ratio, n_qubits(i + 1) / i.bit_length())
        print(max_ratio)

    def test_mean_ratio(self):
        sum = 0
        max = 100000
        for i in range(1, max):
            ratio = n_qubits(i + 1) / i.bit_length()
            sum += ratio
        print(sum / (max - 1))

    def test_n_qubits(self):
        for i in range(1, 100):
            if n_qubits(i) > 5:
                print("Exceeded 8 at %d" % i)
                break


def test_map_bitstring_to_dice(self):
    self.assertEqual(7, dice.map_bitstring_to_dice('1111', 7))
    self.assertEqual(6, dice.map_bitstring_to_dice('0111', 7))
    self.assertEqual(6, dice.map_bitstring_to_dice('111', 6))
    self.assertEqual(3, dice.map_bitstring_to_dice('011', 6))
    self.assertEqual(3, dice.map_bitstring_to_dice('11', 3))
    


def roll_dice_n_shot(n):
    nq = dice.n_qubits(n)

    if nq > 5:
        print("Can't roll a dice that big")
        exit(1)
    qc = dice.make_circuit(n, nq)
    job = executor.execute(qc, 1024, False)
    job_monitor(job)
    counts = job.result().get_counts()
    print(counts)
    results = {}
    for k, v in counts.items():
        side = dice.map_bitstring_to_dice(k[::-1], n)
        if side in results:
            results[side] = results[side] + v
        else:
            results[side] = v
    print(results)


def n_qubits(n):
    if n < 2:
        return 0
    elif n % 2 == 0:
        return n_qubits(int(n / 2)) + 1
    else:
        return n_qubits(n - 1) + 1
