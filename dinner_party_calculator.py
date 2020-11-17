from quantum_setup import *


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

    # Execute the dinner_calculator
    # Max 4 qubits can be used on a Quantum Computer right now (+1 scratch qubit, so in total 5)
    trys = 1024
    qubits = None
    ibmq = False
    required_backend = None

    print("Execute the following command:")
    print(" Number of trys: " + str(trys))
    print(" Number of qubits: " + str(qubits))
    print(" IBMQ Backend Required: " + str(ibmq))
    print(" Specific IBMQ Backend Required: " + str(required_backend))

    quantum_instance = get_quantumcomputer_quantum_instance(trys, qubits, ibmq, required_backend)

    dinner_result = dinner_calculator.run(quantum_instance)

    if quantum_instance.is_simulator:
        print("As a simulator was selected, no job monitor will be shown.")
    else:
        print("Running on IBMQ")
        print(job_monitor(dinner_result))

    # Plot the final Histrogram
    plot_histogram(dinner_result['measurement'], title="Possible Party Combinations")


if __name__ == '__main__':

    dinner_party_using_grover()

    plt.show()
