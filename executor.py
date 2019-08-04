import qiskit
from qiskit import Aer
from qiskit.providers.ibmq import least_busy, IBMQ


def get_ibm_qc(n_qubits):
    provider = IBMQ.load_account()
    backend = provider.backends(filters=lambda
        x: x.configuration().n_qubits >= n_qubits and not x.configuration().simulator and x.status().operational)
    if len(backend) == 0:
        raise Exception("No backend found with the given constraints")
    return least_busy(backend)


def execute(qc, shots, run_on_real):
    n_qubits = len(qc.qubits)
    device = get_ibm_qc(n_qubits) if run_on_real else Aer.get_backend('qasm_simulator')

    return qiskit.execute(qc, device, shots=shots)
