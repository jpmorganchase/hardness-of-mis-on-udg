In this folder you will find the modules required to optimize instances crated by jpmc-aws-rydbergatoms/generator/generator.py using CPLEX and Docplex with Python. 


create_file.py created the .csv file with the columns that we want to store the results from the optimizations
opt_result.py it contains a class whose responsibility is to store the information into the .csv file created above 
optimizer.py it contains the OptimizerER class that is responsible for looking for the lp file corresponding to the problem instance and execute CPLEX and return the results in an object whose class is Result, and it is defined in the module listed above. 
run_cplex.py here it occurs the actual call to CPLEX using Docplex. 

Then we have variations of these files that we used for the experiments of rewiring (gradual transition from union-jack UDG graph to pure Erdos Renyi graph by incrementally rewiring edges) and for optimizing Erdos Renyi (ER) graphs.

The subfolders are:

data: it contains the data obtained from optimization with different methods and the degeneracy of different problem instances. 
instances: it contains folder for each size of L and inside them, for different optimization instances. 
julia_script: scripts using Julia to get degeneracy of the MIS of problem instances. 
breaking_ud_structure: it contains the code and the notebook to generate the instances for the rewiring experiments.

© 2023 Amazon Web Services, Inc.
Developed as part of an engagement with JPMorgan Chase & Co. 