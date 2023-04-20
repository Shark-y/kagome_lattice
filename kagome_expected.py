import numpy as np
from time import time

import retworkx as rx
from qiskit_nature.problems.second_quantization.lattice import Lattice

# Custom Heisenberg couplings
from heisenberg_model import HeisenbergModel

def get_groud_state () :                                
    ################## Qiskit nature kagome unit cell
    # Kagome unit cell
    num_sites 	= 12

    # Edge weight
    t 			= 1.0

    # Generate graph of kagome unit cell
    # Start by defining all the edges
    graph 		= rx.PyGraph(multigraph=False)
    graph.add_nodes_from(range(num_sites))

    # --- lattice geometry
    """
    edge_list = [
        (0, 1, t),
        (1, 2, t),
        (2, 3, t),
        (3, 4, t),
        (4, 5, t),
        (5, 0, t),
        (0, 6, t),
        (1, 6, t),
        (1, 7, t),
        (2, 7, t),
        (2, 8, t),
        (3, 8, t),
        (3, 9, t),
        (4, 9, t),
        (4, 10, t),
        (5, 10, t),
        (5, 11, t),
        (0, 11, t),
    ]
    """
    start 		= 0
    end 		= 6	
    edge_list 	= [(i, i + 1, t) if i < end - 1 else (end - 1, start, t) for i in range(start, end, 1)  ]

    list1 		= []
    j 			= end
    for i in range(end - 1):
        list1.append((i+1, j, t))
        list1.append((i+1, j+1, t))
        j += 1

    list1.append((start, end, t))
    list1.append((start, j, t))
        
    #print (list1)	
    edge_list.extend(list1)

    #print (edge_list)

    # Generate graph from the list of edges
    graph.add_edges_from(edge_list)

    # Make a Lattice from graph
    kagome_unit_cell = Lattice(graph)

    # Draw Lattice
    #kagome_unit_cell.draw(style={'node_color':'purple'})
    #plt.savefig('kagome_unit_cell.png')

    # ----- place each term in the Hamiltonian on its corresponding edge. 
    from qiskit_nature.mappers.second_quantization import LogarithmicMapper

    # Build Hamiltonian from graph edges
    heis = HeisenbergModel.uniform_parameters(
        lattice=kagome_unit_cell,
        uniform_interaction=1.0,  # same spin-spin interaction weight as used in graph
        uniform_onsite_potential=0.0,  # No singe site external field
    )

    # The Lattice needs an explicit mapping to the qubit states.
    # We map 1 qubit for 1 spin-1/2 particle using the LogarithmicMapper
    log_mapper = LogarithmicMapper()

    # Multiply by factor of 4 to account for (1/2)^2 terms from spin operators in the HeisenbergModel
    ham = 4 * log_mapper.map(heis.second_q_ops().simplify())

    # Print Hamiltonian to check it's what we expect.
    # There are 18 edges and 3 terms per edge (XX, YY, and ZZ),
    # so there should be 54 equally weighted terms.
    #print (ham)


    from qiskit.algorithms import NumPyEigensolver

    # find the first three (k=3) eigenvalues
    exact_solver = NumPyEigensolver(k=3)
    exact_result = exact_solver.compute_eigenvalues(ham)
    #print(exact_result.eigenvalues)

    ############ Compute ground state energy
    # Save ground state energy for later
    gs_energy = np.round(exact_result.eigenvalues[0], 4)
    return gs_energy
    

