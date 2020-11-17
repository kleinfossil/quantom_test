from quantum_setup import *


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


if __name__ == '__main__':
    circuit_trys = 1024
    number_of_qubits = 3
    cir = grover_prep(number_of_qubits)

    cir.draw(output='mpl')

    # --Execute on the quantom simulator--
    execute_quantum_circuit(cir=cir, shots=circuit_trys, use_ibmq=False)

    plt.show()
