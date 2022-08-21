#!/bin/bash


#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=40gb		        # RAM memory to reserve
#SBATCH --partition=express     # partition to submit job to # test node: express
#SBATCH --time=2:00:00          # max wallclock time (i.e. job exec time limit)


#SBATCH --job-name=create_model_dt_grid_search    # only ~30 characters shown when using squeue 
#SBATCH --output=lin_reg_grid_search_1_cpus_list_input_10000_rows_model_select.dat   # important for debugging etc!! name individually
#SBATCH --mail-type=ALL         # receive email for start | finish | abortion
#SBATCH --mail-user=a_lier03@uni-muenster.de

# Instead of Module Loading here, load them prior to execution and run script as "bash -i <script_name>.sh"
# load needed modules
module load palma/2021a         # short version with "ml" also possible: ml palma/2020b
module load GCC/10.3.0
module load OpenMPI/4.1.1
module load Python/3.9.5
module load scikit-learn/0.24
# module laod SQLite/3.35.4

export OMP_PROC_BIND=TRUE
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export NUMEXPR_MAX_THREADS=$SLURM_CPUS_PER_TASK

echo    # functions like a print()-call; here, it creates a blank line, because no text is provided

# run the application(s)

# explicit job to run, e.g. python

#python ../src/test.py
python ../src/regression_analysis/regression_analysis.py



echo
echo "Finished."
echo