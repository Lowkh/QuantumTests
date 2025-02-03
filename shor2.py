from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
import math
import random
from qiskit.circuit.library import QFT

#QiskitRuntimeService.save_account(channel="ibm_quantum", token="<insert token here>")
#service = QiskitRuntimeService()

service = QiskitRuntimeService()

# Function to compute gcd (greatest common divisor)
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

# Function to create the modular exponentiation circuit a^x % N
def modular_exponentiation(a, N, num_qubits):
    """Create the modular exponentiation circuit for a^x % N."""
    qc = QuantumCircuit(num_qubits)
    
    # Placeholder for modular exponentiation logic using basic quantum gates
    # We'll simulate the modular exponentiation using controlled rotations

    for i in range(num_qubits):
        # Using RZ gates to simulate exponentiation (this is a placeholder)
        # A real modular exponentiation would require more advanced logic
        qc.rz(a, i)  # Apply a single qubit rotation

        # Use controlled-X (CX) gates to simulate controlled modular exponentiation
        qc.cx(i, (i + 1) % num_qubits)  # Apply controlled-X gate

    return qc

# Create Shor's quantum circuit for N and a
def create_shors_circuit(N, a):
    num_qubits = math.ceil(math.log(N, 2)) * 2  # Number of qubits for modular exponentiation
    qc = QuantumCircuit(num_qubits, num_qubits)

    # Initialize the first register in state |0> and apply Hadamard gates
    qc.h(range(num_qubits // 2))

    # Apply modular exponentiation U^x mod N
    mod_exp_circuit = modular_exponentiation(a, N, num_qubits // 2)
    qc.append(mod_exp_circuit, range(num_qubits // 2))

    # Apply quantum Fourier transform (QFT)
    qc.append(QFT(num_qubits // 2), range(num_qubits // 2))

    # Measurement step
    qc.measure(range(num_qubits // 2), range(num_qubits // 2))

    return qc

# Run Shor's algorithm using IBM Quantum backend via QiskitRuntimeService and submit the job manually
def run_shors_algorithm_with_runtime(N):
    # Step 1: Classical step - find a random 'a' such that 1 < a < N
    a = random.randint(2, N - 1)
    while gcd(a, N) != 1:
        a = random.randint(2, N - 1)
    
    # Step 2: Create quantum circuit for Shor's algorithm
    qc = create_shors_circuit(N, a)

    # Step 3: Use the least busy operational backend (excluding simulators)
    backend = service.least_busy(operational=True, simulator=False)
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_circuit = pm.run(qc)
    # Step 5: Wait for the job to complete and retrieve the results
    sampler = Sampler(backend)
    job = sampler.run([isa_circuit])
    print(f"Job ID is {job.job_id()}")
    result = job.result()
    pub_result = result[0]
    return pub_result.data.c.get_counts()

# Factorize a number using Shor's algorithm with runtime service optimizations
N = 3233
factors = run_shors_algorithm_with_runtime(N)

# Print the results
print(f"Factors of {N} are: {factors}")
