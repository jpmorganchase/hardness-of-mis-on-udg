The results show in this folder in terms of time (TTS and TTO) and solution were obtained by executing CPLEX for optimizing the problem instances in lp files. These lp files were generated using jpmc-aws-rydbergatoms/generator/generate_all.sh code or similar versions of this that are explained in detail below. CPLEX was executed an Intel Skylake E5 2686 v5  with 8 vCPUs. 

The columns of the .csv files:

'L': length of lattice (lattice of LxL)
'Density': node filling ratio in the lattice 
'Seed': number that refers to the seed used to make the problem instance
'UDG Radius': the radius of the unit-disk graph (UDG). For a given node, we make a cirle with this UDG radius, and we connect this node with all the other nodes within the circle.
'CPLEX TTO': time-to-optimality obtained with CPLEX and reported by CPLEX itself 
'Process TTO': this is the process time-to-optimality that is obtained using the time library in Python and the attribute .process_time()
'Clock TTO': this is the clock time-to-optimality that is obtained using the time library in Python and the attribute .time()
'CPLEX TTS': 
'Process TTS':
'Clock TTS':
'Solution':

Please refer to jpmc-aws-rydbergatoms/generator/optimization/run_cplex.py to see the way that TTO and TTS were calculated using CPLEX. 

Some comments about the different folders: 

Folder diff_radius_UDG: in this folder we store all the results about changing the radius of the unit-disk graph (UDG). These graphs are defined by radius, L (length of grid) and d (filling ratio). There are results for different values of the parameters. 
The notebooks that actually plot these results are jpmc-aws-rydbergatoms/exploratory_notebooks/analyze_runtime_cplex_radius3.ipynb, jpmc-aws-rydbergatoms/exploratory_notebooks/diff_radius_for_UDG.ipynb and jpmc-aws-rydbergatoms/exploratory_notebooks/final_plot_diff_radius_L21.ipynb

scaling_with_size: in this folder we store the scaling of TTS as a function of the size for different optimization instances with density filling = 0.8 and a UDG radius = 3. 

transition_to_ER: here we store all the results regarding the experiment of rewiring the edges from a UDG with radius sqrt(2), which is a union-jack topology, to a pure random Erdos-renyi (ER) graph with the corresponding probability. For L21_rewired_final.csv we report the fraction of edges rewired using a number between 1 and 20, where 1 means 5% rewired and 20, 100% rewired and the increment for each number of a 5%. 
These optimization instances (lp files) were obtained by executing the notebook jpmc-aws-rydbergatoms/generator/breaking_ud_structure/get_lp_files_for_moving.ipynb. The ER instances were obtained with the notebook jpmc-aws-rydbergatoms/generator/breaking_ud_structure/get_lp_for_ER.ipynb.