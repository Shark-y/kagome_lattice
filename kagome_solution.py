from kagome_expected import get_groud_state
from kagome_lattice import KagomeLattice
import argparse
import matplotlib.pyplot as plt

"""
usage: kagome_solution.py [-h] [-p PROVIDER] [-b RUNBACKEND] [-t TRANSPILE_BACKEND] [-q NUM_QUBITS]
                          [-s SHOTS] [-a {ExcitationPreserving,EfficientSU2,PauliTwoDesign,TwoLocal,RealAmplitudes}]
                          [-o {SPSA,SLSQP,COBYLA,UMDA,GSLS,GradientDescent,L_BFGS_B,NELDER_MEAD,POWELL,NFT}]
                          [-i MAX_ITER] [-ol {1,2,3}] [-ui UNIFORM_INTERACTION] [-up UNIFORM_POTENTIAL]
                          [-r {T-REx,ZNE,PEC}] [-w WEIGHT] [-v {1,2,3,4}]

optional arguments:
  -h, --help            show this help message and exit
  -p, --provider PROVIDER   Hub/Group/Project (default: ibm-q-community/ibmquantumawards/open-science-22)
  -b RUNBACKEND, --runbackend RUNBACKEND
                        Run backend
  -t TRANSPILE_BACKEND, --transpile_backend TRANSPILE_BACKEND
                        Transpile backend
  -q NUM_QUBITS, --num_qubits NUM_QUBITS
                        Run backend # of qubits
  -s SHOTS, --shots SHOTS
                        Shots
  -a {ExcitationPreserving,EfficientSU2,PauliTwoDesign,TwoLocal,RealAmplitudes}, --ansatz_type {ExcitationPreserving,EfficientSU2,PauliTwoDesign,TwoLocal,RealAmplitudes}
                        Ansatz type
  -o {SPSA,SLSQP,COBYLA,UMDA,GSLS,GradientDescent,L_BFGS_B,NELDER_MEAD,POWELL,NFT}, --optimizer_type {SPSA,SLSQP,COBYLA,UMDA,GSLS,GradientDescent,L_BFGS_B,NELDER_MEAD,POWELL,NFT}
                        Optimizer type
  -i MAX_ITER, --max_iter MAX_ITER
                        Maximum number of iterations
  -ol {1,2,3}, --opt_level {1,2,3}
                        Optimization level
  -ui UNIFORM_INTERACTION, --uniform_interaction UNIFORM_INTERACTION
                        HeisenbergModel uniform interaction
  -up UNIFORM_POTENTIAL, --uniform_potential UNIFORM_POTENTIAL
                        HeisenbergModel uniform potential
  -r {T-REx,ZNE,PEC}, --resilience_type {T-REx,ZNE,PEC}
                        Resilience type
  -w WEIGHT, --weight WEIGHT
                        Edge weight
  -v {1,2,3,4}, --verbosity {1,2,3,4}
                        Verbosity level
Examples:
1. Run in inbq_guadalupe with ansatz: EfficientSU2, Optimizer: SPSA, edge weight of 1.3, 2048 shots, resilience: ZNE
   # python3 kagome_solution.py -a EfficientSU2 -w 1.3 >> out-guadalupe.txt &
2. Run with a POWELL optimizer and uniform potential
   # python3 kagome_solution.py -a EfficientSU2 -o POWELL -up -1.0 -s 4096 >> out-guadalupe.txt &
3. Run tin the sate simulator with default params:
   # python3 kagome_solution.py -b simulator_statevector
"""
# Args, use -h to view
parser  = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

# ibm-q-community/ibmquantumawards/open-science-22
parser.add_argument('-p', '--provider',      help="Connection Provider: Hub/Group/Project"
    ,  default='ibm-q-community/ibmquantumawards/open-science-22')

parser.add_argument('-b', '--runbackend',           help="Run backend",  default='ibmq_guadalupe')
parser.add_argument('-t', '--transpile_backend',    help="Transpile backend",  default='ibmq_guadalupe')

parser.add_argument('-q', '--num_qubits',       type=int, help="Run backend # of qubits",  default=16)
parser.add_argument('-s', '--shots',            type=int, help="Shots",  default=2048)

parser.add_argument('-a', '--ansatz_type',      help="Ansatz type"
    , default='EfficientSU2'
    , choices=['ExcitationPreserving', 'EfficientSU2','PauliTwoDesign','TwoLocal','RealAmplitudes'])
    
parser.add_argument('-o', '--optimizer_type',   help="Optimizer type"
    , default='NFT'
    , choices=['SPSA', 'SLSQP','COBYLA','UMDA','GSLS','GradientDescent','L_BFGS_B','NELDER_MEAD','POWELL','NFT'])
parser.add_argument('-i', '--max_iter',         help="Maximum number of iterations", type=int, default=100)

parser.add_argument('-ol', '--opt_level',           help="Optimization level", type=int, default=1, choices=range(1, 4))
parser.add_argument('-ui', '--uniform_interaction', help="HeisenbergModel uniform interaction", type=float)
parser.add_argument('-up', '--uniform_potential',   help="HeisenbergModel uniform potential", type=float, default=0.0)
    
parser.add_argument('-r', '--resilience_type',  help="Resilience type", default='ZNE', choices=['T-REx','ZNE','PEC'])
parser.add_argument('-w', '--weight',           help="Edge weight", type=float, default=1.6)
parser.add_argument('-v', '--verbosity',        help="Verbosity level", type=int, default=2, choices=range(1,5))

args        = parser.parse_args()
cn          = args.provider.split("/")     # Connection string hub/group/project

# Expected
gs_energy   = get_groud_state()

print("Ground state energy: %.2f" % gs_energy)
#print (lattice)

lattice     = KagomeLattice(weight=args.weight, ansatz_type=args.ansatz_type
                , optimizer_type=args.optimizer_type
                , optimizer_maxiter=args.max_iter
                , resilience_type=args.resilience_type)

lattice.expected_energy = gs_energy

run_params  = { 
    'hub'                   : cn[0],    # args.hub,
    'group'                 : cn[1],    # args.group, 
    'project'               : cn[2],    # args.project,
    'provider'              : args.provider,
    'transpile_backend'     : args.transpile_backend,
    'run_backend'           : args.runbackend,
    'num_qubits'            : args.num_qubits,
    'qubit_layout'          : [1, 2, 3, 5, 8, 11, 14, 13, 12, 10, 7, 4],
    'shots'                 : args.shots,
    'opt_level'             : args.opt_level,
    'uniform_interaction'   : args.uniform_interaction if args.uniform_interaction != None else args.weight,
    'uniform_potential'     : args.uniform_potential,
    'verbosity'             : args.verbosity
}

# run it
computed_gse, intermediate_info_real_backend = lattice.run(run_params)

def rel_err(target, measured):
    return abs((target - measured) / target)

err_prob    = 100 * rel_err(gs_energy, computed_gse)
    
print(f'Expected ground state energy: {gs_energy:.8f}')
print(f'Computed ground state energy: {computed_gse:.8f}')
print(f'Relative error: {100 * rel_err(gs_energy, computed_gse):.8f} %')

# Let's plot the energy convergence data the callback function acquired.
backend         = args.runbackend
ans_name        = args.ansatz_type
optimizer_name  = args.optimizer_type
resilience      = args.resilience_type
shots           = args.shots
t               = args.weight
plot_name       = "plot-%s-%s-%s-%s-s(%d)-w(%.4f)-e%.2f.png" % (backend, ans_name, optimizer_name, resilience, shots, t, err_prob)
plt.figure(figsize=(10, 5))
plt.plot(intermediate_info_real_backend, color='purple', lw=2, label='VQE')
plt.ylabel('Energy')
plt.xlabel('Iterations')
plt.title(backend + "/" + ans_name + "/" + optimizer_name + "/" + resilience 
        + "/" + str(shots) + " weight: %.4f Error: %.2f %%" % (t,err_prob))
# Exact ground state energy value
plt.axhline(y=gs_energy, color="tab:red", ls="--", lw=2, label="Target: " + str(gs_energy))
plt.legend()
plt.grid()
plt.savefig(plot_name)
