from qiskit import *
from qiskit.tools.visualization import plot_histogram
from qiskit.tools.monitor import job_monitor
import matplotlib.pyplot as plt
import numpy as np
import pylatexenc


def qiskitversion():
    print('Current qiskit Version: ',qiskit.__qiskit_version__)
    print('Current IBM Account: ',IBMQ.load_account())

def quantomcircuit():
    qr = QuantumRegister(2)
    cr = ClassicalRegister(2)
    circuit = QuantumCircuit(qr, cr)
    circuit.h(qr[0])
    circuit.cx(qr[0], qr[1])
    circuit.measure(qr, cr)

    circuit.draw(output='mpl')
    # evenly sampled time at 200ms intervals
    # t = np.arange(0., 5., 0.2)
    return circuit


def quantomsimulator():
    simulator = Aer.get_backend('qasm_simulator')
    return simulator


def quantomcomputer(cir):
    IBMQ.load_account()
    provider = IBMQ.get_provider('ibm-q')
    qcomp = provider.get_backend('ibmq_16_melbourne')
    job = execute(cir, backend=qcomp)
    print(job_monitor(job))
    result = job.result()
    plot_histogram(result.get_counts(cir))


if __name__ == '__main__':
    # qiskitversion()
    cir = quantomcircuit()
    result = execute(cir, backend=quantomsimulator()).result()
    plot_histogram(result.get_counts(cir))
    quantomcomputer(cir)

    plt.show()

