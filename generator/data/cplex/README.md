we ran CPLEX for optimizing the problem instances with density d=0.8 and different L on an Intel Skylake E5 2686 v5  with 8 vCPUs. None command in particular was added to the execution.  
These lp files were generated by running ../../generate_all.sh code. 

Once obtained the log files, we used the notebook in this path open_logs.ipynb to put the relevant data into the .csv files. If you would like to access the log files, please contact Romina Yalovetzky from JPMC. 

Please note that the .csv files that indicate no cuts, this means that the lines ´cplex set mip cuts all -1´ was in the executed in cplex for each optimization. This turns off the generation of all cuts.