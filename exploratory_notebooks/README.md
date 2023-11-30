This folder contains the notebooks that analyze data regarding the TTS and TTO obtained with different Branch-and-bound based optimizers as well an analysis of some characteristics about the graphs for different experiments made. 

Below we briefly describe each module: 

1) jpmc-aws-rydbergatoms/exploratory_notebooks/analyze_runtime_cplex_radius3.ipynb 
We calculate the scaling of TTS for many MIS problems on UDG with radius 3, and we compare with the scaling with the union-jack topology (radius=sqrt(2)). The optimization instances (lp files) were obtained by executing a code similar to jpmc-aws-rydbergatoms/generator/generate_all.sh but passing the argument of r=3:
python3 generate.py -L $L -s $seed -r 3

2) jpmc-aws-rydbergatoms/exploratory_notebooks/final_plot_diff_radius_L21.ipynb 
We plot the TTS as a function of the radius for L (length of lattice) =21 and d (filling ratio) = 0.8. The optimization instances were constructed similarly as on the point above but for all the different radius. 

3) jpmc-aws-rydbergatoms/exploratory_notebooks/transition_to_ER_cplex.ipynb 
We plot the transition for UDG with union-jack topology to a pure Erdos Renyi (ER) graph. This transition is accomplished by rewiring a fraction of edges incrementally. Please refer to jpmc-aws-rydbergatoms/generator/generate_ER.py to see how the lp files of the optimization instance of ER was made and to jpmc-aws-rydbergatoms/generator/generate_rewired_graph.py for the lp files of the instances for the transition.

4) jpmc-aws-rydbergatoms/exploratory_notebooks/analyze_runtime_cplex.ipynb
We plot TTS as a function of the size (N) obtained with CPLEX for the instances obtained using a code similar to the one in 
jpmc-aws-rydbergatoms/generator/generate_all.sh for MIS problems on UDG with union-jack topology. We changed the filling fraction rho that we called density and we plotted as well. We also plot the exponent coefficient as a function of the filling fraction. Refer to Appendix A.4 for more details.

© 2023 Amazon Web Services, Inc.
Developed as part of an engagement with JPMorgan Chase & Co. 