from qiskit import *
from qiskit.tools.visualization import plot_histogram
from qiskit.tools.monitor import job_monitor
import matplotlib.pyplot as plt
import numpy as np
import pylatexenc
from qiskit.quantum_info import Operator
from qiskit import QuantumCircuit
from qiskit import IBMQ
from qiskit.providers.ibmq import least_busy


# Prints out qiskit version and IBM Account Infos
def qiskitversion():
    print('Current qiskit Version: ', qiskit.__qiskit_version__)
    print('Current IBM Account: ', IBMQ.load_account())

# The Quantom Circuit. Make your changes here.


# Executes the QASM Simulator
def quantomsimulator(cir, shots):
    # choose the simulator backend
    simulator = Aer.get_backend('qasm_simulator')

    result = execute(cir, backend=simulator, shots=shots).result()
    plot_histogram(result.get_counts(cir))
    return simulator


# Executes a real Quantom Computer
def quantomcomputer(circ, number_qubits, shots):
    IBMQ.load_account()
    provider = IBMQ.get_provider('ibm-q')

    # Selects the lest busy backend which has enough number_of_qubits and is not a simulator and is operational
    backend = least_busy(provider.backends(filters=lambda x: x.configuration().n_qubits >= (number_qubits+1) and not x.configuration().simulator and x.status().operational == True))

    print("least busy backend ", backend)

    # simple way to get a specific backend
    # backend = provider.get_backend('ibmq_16_melbourne')

    # Executes the job on the selected backedn
    job = execute(circ, backend=backend, shots=shots, optimization_level=3)

    print(job_monitor(job))
    result = job.result()
    plot_histogram(result.get_counts(circ))


def quantomcircuit():
    qr = QuantumRegister(2)
    cr = ClassicalRegister(2)
    circuit = QuantumCircuit(qr, cr)
    circuit.h(qr[0])
    circuit.cx(qr[0], qr[1])
    circuit.measure(qr, cr)

    circuit.draw(output='mpl')
    return circuit


def phase_oracle(n, indices_to_mark, name='Oracle'):
    # create a quantum circuit on n qubits
    qc = QuantumCircuit(n, name=name)

    # create the identity matrix on n qubits
    oracle_matrix = np.identity(2 ** n)
    # add the -1 phase to marked elements
    for index_to_mark in indices_to_mark:
        oracle_matrix[index_to_mark, index_to_mark] = -1

    # convert your matrix (called oracle_matrix) into an operator, and add it to the quantum circuit
    qc.unitary(Operator(oracle_matrix), range(n))

    return qc



def diffuser(n):
    # create a quantum circuit on n qubits
    qc = QuantumCircuit(n, name='Diff - "V"')

    # apply hadamard gates to all qubits
    qc.h(range(n))
    # call the phase oracle applied to the zero state
    qc.append(phase_oracle(n, [0]), range(n))
    # apply hadamard gates to all qubits
    qc.h(range(n))
    return qc


def grover(n, indices_of_marked_elements):

    # Create a quantum circuit on n qubits
    qc = QuantumCircuit(n, n)

    # Determine r - from LAB - didn't work.
    # r = int(np.floor(np.pi/4*np.sqrt(2**n/len(indices_of_marked_elements))))

    # Determine r - from Course
    r = int(np.round(np.pi/(4*np.arcsin(np.sqrt(len(indices_of_marked_elements)/2**n)))-1/2))

    print(f'{n} qubits, basis states {indices_of_marked_elements} marked, {r} rounds')

    # step 1: apply Hadamard gates on all qubits
    qc.h(range(n))

    # step 2: apply r rounds of the phase oracle and the diffuser
    for _ in range(r):
        qc.append(phase_oracle(n, indices_of_marked_elements), range(n))
        qc.append(diffuser(n), range(n))

    # step 3: measure all qubits
    qc.measure(range(n), range(n))

    return qc


if __name__ == '__main__':
    # --Print qiskit version--
    # qiskitversion()

    # --Prepatation Step--
    shots_simulator = 1024
    shots_ibmq = 1024

    # --create a simple quantum circuit--
    # cir = quantomcircuit()

    # --Execute Grover algorithm to find marked elements in an unsorted list--

    # Select number of qubits
    number_of_qubits = 3

    # Create "marked elements". These elements will be the elements the algorithm should look for.
    # In this case the the elements will be chosen randomly based on the number of qubits
    # (number ob qubits in binary means 2^n)
    x = np.random.randint(2**number_of_qubits)
    y = np.random.randint(2**number_of_qubits)

    # this makes sure that the y elements is not equal to x
    while y == x:
        y = np.random.randint(2**number_of_qubits)

    marked = [x,y]

    # Excecutes the grover algorithm and provides back the probabilities than an element was marked
    cir = grover(number_of_qubits, marked)
    cir.draw(output='mpl')

    # --Execute on the quantom simulator--
    quantomsimulator(cir, shots_simulator)

    # --Execute on the quantom computer--
    #quantomcomputer(cir, number_of_qubits, shots_ibmq)

    plt.show()

