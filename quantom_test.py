from qiskit import *
from qiskit.aqua import QuantumInstance
from qiskit.tools.visualization import plot_histogram
from qiskit.tools.monitor import job_monitor
import matplotlib.pyplot as plt
import numpy as np
# import pylatexenc
from qiskit.quantum_info import Operator
from qiskit import QuantumCircuit
from qiskit import IBMQ
from qiskit.providers.ibmq import least_busy


# Prints out qiskit version and IBM Account Infos
def qiskitversion():
    print('Current qiskit Version: ', qiskit.__qiskit_version__)
    print('Current IBM Account: ', IBMQ.load_account())

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
    backend = provider.get_backend('ibmq_16_melbourne')

    print("Will execute circuit on backend: ", backend)

    # Executes the job on the selected backedn
    job = execute(circ, backend=backend, shots=shots, optimization_level=3)

    print(job_monitor(job))
    result = job.result()
    plot_histogram(result.get_counts(circ))


# Selects a IBMQ quantum instance if number of qubits is lower than 5
def get_quantomcomputer_quantum_instance(shots=100, number_qubits=0, use_quantum_computer=False):
    if 0 < number_qubits < 5 and use_quantum_computer:
        IBMQ.load_account()
        provider = IBMQ.get_provider('ibm-q')

        # Selects the lest busy backend which has enough number_of_qubits and is not a simulator and is operational
        backend = least_busy(provider.backends(filters=lambda x: x.configuration().n_qubits >= (number_qubits + 1) and not x.configuration().simulator and x.status().operational == True))
        print("least busy backend ", backend)

        # simple way to get a specific backend
        # backend = provider.get_backend('ibmq_16_melbourne')
        print("The following Backend has be selected: ", backend)

        quantum_instance = QuantumInstance(backend, shots, skip_qobj_validation=False)

        return quantum_instance
    else:
        if use_quantum_computer:
            raise Exception('Sorry your number of qubits reached. The max number is 4. Your requested: ' + str(number_qubits))
        else:
            # choose the simulator backend
            simulator = Aer.get_backend('qasm_simulator')
            simulator_instance = QuantumInstance(simulator, shots)
            print("The following simulator was selected: " + str(simulator_instance.backend_name))
            return simulator_instance


def quantomcircuit():
    qr = QuantumRegister(2)
    cr = ClassicalRegister(2)
    simple_circuit = QuantumCircuit(qr, cr)
    simple_circuit.h(qr[0])
    simple_circuit.cx(qr[0], qr[1])
    simple_circuit.measure(qr, cr)

    simple_circuit.draw(output='mpl')
    return simple_circuit


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


def grover_prep(qubit_number):
    # --Execute Grover algorithm to find marked elements in an unsorted list--

    # Select number of qubits

    # Create "marked elements". These elements will be the elements the algorithm should look for.
    # In this case the the elements will be chosen randomly based on the number of qubits
    # (number ob qubits in binary means 2^n)
    x = np.random.randint(2 ** qubit_number)
    y = np.random.randint(2 ** qubit_number)

    # this makes sure that the y elements is not equal to x
    while y == x:
        y = np.random.randint(2 ** qubit_number)

    marked = [x, y]

    # Excecutes the grover algorithm and provides back the probabilities than an element was marked
    grover_cir = grover(qubit_number, marked)
    return grover_cir


def dinner_party_using_grover():
    # This algorithm will solve the dinner party problem, where you want to invite friends to a dinner party, but
    # not all fit to each other. This results in a logical expression (D can with meet with A or C can meet with B
    # but A and B do not want to meet.
    # The algorithm will use Grover's algorithm to solve this problem.
    # NOTICE: to execute even a small number of elements, the algorithm will need at least 11 qubits
    # which most IBMQ backends don't provide.

    # Here an overview of an example:
    # Example Table for a simple expression: log_expr = '((D & A) | (C & B)) & ~(A & B)'
    # D | C | B | A | Result
    # - - - - - - - - - - - -
    # 0 | 0 | 0 | 0 | 0
    # 1 | 0 | 0 | 0 | 0
    # 0 | 1 | 0 | 0 | 0
    # 1 | 1 | 0 | 0 | 0
    # 0 | 0 | 1 | 0 | 0
    # 1 | 0 | 1 | 0 | 0
    # 0 | 1 | 1 | 0 | 1
    # 1 | 1 | 1 | 0 | 1
    # 0 | 0 | 0 | 1 | 0
    # 1 | 0 | 0 | 1 | 1
    # 0 | 1 | 0 | 1 | 0
    # 1 | 1 | 0 | 1 | 1
    # 0 | 0 | 1 | 1 | 0
    # 1 | 0 | 1 | 1 | 0
    # 0 | 1 | 1 | 1 | 0
    # 1 | 1 | 1 | 1 | 0

    # In the later plot results are organized alphabetically
    # starting with the least significant bit (...1 = A; ..1. = B; .1.. = C; 1... = D; and so on)
    # Example: 0110 shows the probability B and C would be a possible combination

    from qiskit.aqua.algorithms import Grover
    from qiskit.aqua.components.oracles import LogicalExpressionOracle
    from qiskit.tools.visualization import plot_histogram

    # Logical Expressions which can be used for the LogicalExpressionOracle: & = and; | = or; ~ = not; ^ = xor
    log_expr = '((D & A) | (C & B)) & ~(A & B)'

    dinner_calculator = Grover(LogicalExpressionOracle(log_expr))

    # Execute on Simulator
    # dinner_result = dinner_calculator.run(Aer.get_backend('qasm_simulator'))
    # Execute on Quantom Computer
    # Max 4 qubits can be used right now (+1 scratch qubit, so in total 5)
    trys = 1024

    # Executes on Simulator if no qubit number is provided
    quantum_instance = get_quantomcomputer_quantum_instance(trys)

    dinner_result = dinner_calculator.run(quantum_instance)

    if quantum_instance.is_simulator:
        print("As simulator was selected, no job monitor will be shown.")
    else:
        print("Running on IBMQ")
        print(job_monitor(dinner_result))

    # Plot the final Histrogram
    plot_histogram(dinner_result['measurement'], title="Possible Party Combinations")


if __name__ == '__main__':
    # --Print qiskit version--
    # qiskitversion()

    # --Prepatation Step--
    # shots_simulator = 1024
    # shots_ibmq = 1024

    # --create a simple quantum circuit--
    # cir = quantomcircuit()

    # number_of_qubits = 3
    # cir = grover_prep(number_of_qubits)

    # cir.draw(output='mpl')

    # --Execute on the quantom simulator--
    # quantomsimulator(cir, shots_simulator)

    # --Execute on the quantom computer--
    # quantomcomputer(cir, number_of_qubits, shots_ibmq)

    dinner_party_using_grover()

    plt.show()

