import numpy as np
from time import time
import retworkx as rx
import pprint
from qiskit import IBMQ
from qiskit import BasicAer
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Parameter
from qiskit.circuit.library import EfficientSU2,ExcitationPreserving,RealAmplitudes,TwoLocal
from qiskit_nature.problems.second_quantization.lattice import Lattice
from qiskit.algorithms.optimizers import COBYLA,SPSA,SLSQP,GSLS,GradientDescent,L_BFGS_B,NELDER_MEAD,NFT,POWELL,QNSPSA,SciPyOptimizer,UMDA
from qiskit_ibm_runtime import (QiskitRuntimeService,Session,Options,Estimator as RuntimeEstimator)

from heisenberg_model import HeisenbergModel
from custom_vqe import CustomVQE
from qiskit_nature.mappers.second_quantization import LogarithmicMapper
from qiskit.circuit.library import EfficientSU2, ExcitationPreserving, RealAmplitudes,TwoLocal,PauliTwoDesign

"""
Kagome Lattice class
"""
class KagomeLattice:
    ExcitationPreserving = 'ExcitationPreserving'
    EfficientSU2         = 'EfficientSU2'
    PauliTwoDesign       = 'PauliTwoDesign'
    TwoLocal             = 'TwoLocal'
    RealAmplitudes       = 'RealAmplitudes'
    
    OPT_SPSA            = 'SPSA'
    OPT_SLSQP           = 'SLSQP'
    OPT_COBYLA          = 'COBYLA'
    OPT_UMDA            = 'UMDA'
    OPT_GSLS            = 'GSLS'
    OPT_GradientDescent = 'GradientDescent'
    OPT_L_BFGS_B        = 'L_BFGS_B'
    OPT_NELDER_MEAD     = 'NELDER_MEAD'
    OPT_POWELL          = 'POWELL'
    OPT_NFT             = 'NFT'
    
    expected_energy     = 0
    
    def __init__(self, qubits=12, weight=1.0, ansatz_type=ExcitationPreserving
        , optimizer_type='SPSA', optimizer_maxiter=200, resilience_type='ZNE'):
        """
        Args:
            qubits      : # of qubits
            weight      : Lattice edge weigth
            ansatz_type : Ansatz type (string): ExcitationPreserving,EfficientSU2,PauliTwoDesign,TwoLocal,RealAmplitudes
            optimizer_type : Optimizer (string) SPSA,SLSQP,COBYLA,UMDA,GSLS,GradientDescent,L_BFGS_B,NELDER_MEAD,POWELL,NFT
            optimizer_maxiter: max # of iteractions/function evals of the optimizer.
            resilience_type: Error correction mode T-REx (1),ZNE (2),PEC (3)
        """
        self._ans_type           = ansatz_type
        self._optimizer_type     = optimizer_type
        self._optimizer_maxiter  = optimizer_maxiter
        self._resilience_type    = resilience_type
        self._weight             = weight

        # default ansatz
        if ansatz_type == KagomeLattice.ExcitationPreserving :
            self._ansatz    = ExcitationPreserving(qubits, reps=1, entanglement='linear').decompose()
        elif ansatz_type == KagomeLattice.EfficientSU2 :
            self._ansatz    = EfficientSU2(qubits, entanglement='reverse_linear'
                , reps=1, skip_final_rotation_layer=True).decompose()
        elif ansatz_type == KagomeLattice.PauliTwoDesign :
            self._ansatz    = PauliTwoDesign(qubits, reps=1).decompose()
        elif ansatz_type == KagomeLattice.TwoLocal :
            self._ansatz    = TwoLocal(qubits, 'ry', 'cx', 'linear', reps=2, insert_barriers=True)
        elif ansatz_type == KagomeLattice.RealAmplitudes :
            self._ansatz    = RealAmplitudes(qubits, reps=1, entanglement='linear', insert_barriers=True)
        else :
            raise Exception("Invalid ansatz type ", ansatz_type)

        # default optimizers
        if optimizer_type == KagomeLattice.OPT_SPSA :
            self._optimizer    = SPSA(maxiter=optimizer_maxiter)    # default: 100
        elif optimizer_type == KagomeLattice.OPT_SLSQP :
            self._optimizer    = SLSQP(maxiter=optimizer_maxiter)
        elif optimizer_type == KagomeLattice.OPT_COBYLA :
            self._optimizer    = COBYLA(maxiter=optimizer_maxiter)  # default:75
        elif optimizer_type == KagomeLattice.OPT_UMDA :
            self._optimizer    = UMDA(maxiter=optimizer_maxiter)
        elif optimizer_type == KagomeLattice.OPT_GSLS :
            self._optimizer    = GSLS(maxiter=optimizer_maxiter)
        elif optimizer_type == KagomeLattice.OPT_GradientDescent :
            self._optimizer    = GradientDescent(maxiter=optimizer_maxiter)
        elif optimizer_type == KagomeLattice.OPT_L_BFGS_B :
            self._optimizer    = L_BFGS_B(maxfun=optimizer_maxiter)
        elif optimizer_type == KagomeLattice.OPT_NELDER_MEAD :
            self._optimizer    = NELDER_MEAD(maxfev=optimizer_maxiter)    # default: 1000's
        elif optimizer_type == KagomeLattice.OPT_POWELL :
            self._optimizer    = POWELL(maxfev=optimizer_maxiter)         # default: 1000's
        elif optimizer_type == KagomeLattice.OPT_NFT :
            self._optimizer    = NFT(maxfev=optimizer_maxiter)
        else :
            raise Exception("Invalid optimizer name ", optimizer_type)
            
    
    def __str__(self):
        return f"{self._ansatz} {self._optimizer}" 

    
    def get_resilience_level (self) :
        # 1 = T-REx, 2 = ZNE, 3 = PEC
        if      self._resilience_type == 'ZNE':    return 2
        elif    self._resilience_type == 'PEC':    return 3
        elif    self._resilience_type == 'T-REx':  return 1
        raise Exception("Invalid resilience name ", self.resilience)
    
    
    def get_cell_graph (self, num_qubits) :
        # Generate graph of kagome unit cell
        # Start by defining all the edges
        t           = self._weight
        graph_16    = rx.PyGraph(multigraph=False)
        graph_16.add_nodes_from(range(num_qubits))
        edge_list   = [
            (1, 2, t),
            (2, 3, t),
            (3, 5, t),
            (5, 8, t),
            (8, 11, t),
            (11, 14, t),
            (14, 13, t),
            (13, 12, t),
            (12, 10, t),
            (10, 7, t),
            (7, 4, t),
            (4, 1, t),
            (4, 2, t),
            (2, 5, t),
            (5, 11, t),
            (11, 13, t),
            (13, 10, t),
            (10, 4, t),
        ]
        # Generate graph from the list of edges
        graph_16.add_edges_from(edge_list)

        # Make a Lattice from graph
        kagome_unit_cell_16 = Lattice(graph_16)
    
        return kagome_unit_cell_16
        
    def get_hamiltonian (self, num_qubits, uniform_interaction, uniform_potential=0.0 ) :
        # Build Hamiltonian from graph edges
        #t                       = self._weight
        kagome_unit_cell_16     = self.get_cell_graph (num_qubits)
        heis_16                 = HeisenbergModel.uniform_parameters(
            lattice=kagome_unit_cell_16,
            uniform_interaction=uniform_interaction, # t,
            uniform_onsite_potential=uniform_potential #0.0,  # No singe site external field
        )

        # Map from SpinOp to qubits just as before.
        log_mapper  = LogarithmicMapper()
        ham_16      = 4 * log_mapper.map(heis_16.second_q_ops().simplify())
        return ham_16
        
    def run(self, env = None) :
        transpile_backend   = env['transpile_backend']
        num_qubits          = env['num_qubits']
        q_layout            = env['qubit_layout']
        run_backend         = env['run_backend']
        shots               = env['shots']
        opt_level           = env['opt_level']
        uniform_interaction = env['uniform_interaction']
        uniform_potential   = env['uniform_potential']
        verbosity           = env['verbosity']
        
        if verbosity > 0 :
            print('Backend    : %s' % (run_backend))
            print('Ansatz     : %s' % (self._ans_type))
            print('Optimizer  : %s Maxiter: %d' % (self._optimizer_type, self._optimizer_maxiter))
            print('Resilience : %s shots: %d Weight: %.4f' % (self._resilience_type , shots, self._weight))
            print('Optim lev  : %d uniform_potential: %.4f' % (opt_level, uniform_potential))
        if verbosity > 1 :
            pprint.pprint(env)
        
        ## 3-2 Qiskit runtime Real backend (ibmq_guadalupe)
        provider        = IBMQ.load_account()
        provider        = IBMQ.get_provider(hub=env['hub'], group=env['group'], project=env['project'])
        service         = QiskitRuntimeService(channel='ibm_quantum', instance=env['provider'])
        
        # run options
        options 					= Options()
        options.resilience_level 	= self.get_resilience_level() # 1 = T-REx, 2 = ZNE, 3 = PEC
        options.optimization_level 	= opt_level # 1 , 0 = No optimization
        options.execution.shots 	= shots
 
        # Real backend; needed for transpilation later on
        real_backend                = provider.get_backend(transpile_backend)
 
        # Match qubit layout
        # Force anstaz to be applied to qubits in the heavy hex.
        # Avoid the outer qubits 0, 6, 9, and 15 which we accounted for in the lattice definition.
        ansatz_opt                  = transpile(self._ansatz, backend=real_backend, initial_layout=q_layout)
        
        if verbosity > 2 :
            print('Number and type of gates in the cirucit:', ansatz_opt.count_ops())
            print('Number of parameters in the circuit:', ansatz_opt.num_parameters)

        # Define a simple callback function
        intermediate_info_real_backend = []
        def callback_real(value):
                intermediate_info_real_backend.append(value)

        ham_16      = self.get_hamiltonian(num_qubits, uniform_interaction, uniform_potential)
        if verbosity > 3 :
            print(ham_16)
        
        start       = time()
        with Session(service=service, backend=run_backend) as session:
            # Prepare primitive
            rt_estimator    = RuntimeEstimator(session=session, options=options)
            
            # set up algorithm
            custom_vqe      = CustomVQE(rt_estimator, ansatz_opt, self._optimizer, callback=callback_real)
            custom_vqe.set_expected_values(self.expected_energy, 1, uniform_interaction, num_qubits, q_layout)

            # run algorithm
            result          = custom_vqe.compute_minimum_eigenvalue(ham_16)
        end         = time()

        # Compute the relative error between the expected ground state energy and the measured
        computed_gse 	= intermediate_info_real_backend[-1]

        if verbosity > 1 :
            print(f'Execution time (s): {end - start:.2f}')
            print(result)
            print(f'Computed ground state energy: {computed_gse:.8f}')
            print(f'Result eigen value: {result.eigenvalue:.8f}')
        
        return computed_gse, intermediate_info_real_backend