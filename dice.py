import argparse

import math
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.tools.monitor import job_monitor

import executor

run_on_real = False


def roll_dice(n):
    nq = n_qubits(n)
    if nq > 16:
        print("Can't roll a dice that big")
        exit(1)
    qc = make_circuit(n, nq)
    job = executor.execute(qc, 1, run_on_real)
    job_monitor(job)
    counts = job.result().get_counts()
    return map_bitstring_to_dice(next(iter(counts)), n)


def make_circuit(n, nq):
    q = QuantumRegister(nq)
    c = ClassicalRegister(nq)
    qc = QuantumCircuit(q, c)
    make_circuit_helper(qc, q, n)
    for i in range(nq):
        qc.measure(q[i], c[i])
    return qc


def map_bitstring_to_dice(bitstring, n):
    if n < 2:
        return n
    elif n % 2 == 0:
        recurse = map_bitstring_to_dice(bitstring[1:], int(n / 2))  # TODO rename
        if bitstring[0] == '1':
            return recurse + int(n / 2)
        return recurse
    else:
        recurse = map_bitstring_to_dice(bitstring[1:], n - 1)
        if bitstring[0] == '1':
            return n
        return recurse


def make_circuit_helper(qc, q, n):
    if n < 2:
        return
    elif n % 2 == 0:
        qc.h(q[0])
        make_circuit_helper(qc, q[1:], int(n / 2))
    else:
        desired_vector = [math.sqrt(n - 1) / math.sqrt(n), 1 / math.sqrt(n)]
        qc.initialize(desired_vector, [q[0]])  # alternatively qc.u3(2 * math.acos(1 / math.sqrt(3)), 0, 0, q[0])
        make_circuit_helper(qc, q[1:], n - 1)


def n_qubits(n):
    if n < 2:
        return 0
    elif n % 2 == 0:
        return n_qubits((n / 2)) + 1
    else:
        return n_qubits(n - 1) + 1


def main():
    parser = argparse.ArgumentParser(description='Roll an n sided dice')
    parser.add_argument('n', help='Number of sides', type=int, action='store')  # TODO validate input
    parser.add_argument('-r', dest='real', default=False, action='store_true',
                        help='Run on real quantum computer')
    args = parser.parse_args()
    global run_on_real
    run_on_real = args.real
    print(roll_dice(args.n))


if __name__ == '__main__':
    main()
