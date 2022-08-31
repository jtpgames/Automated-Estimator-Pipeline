#!/bin/bash
 
#SBATCH --partition=express
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=6
#SBATCH --mem=1G
#SBATCH --time=00:10:00
#SBATCH --job-name=jupyter-notebook
#SBATCH --output=jupyter-notebook-%J.log
 
echo "------------------------------------------------------------"
echo "SLURM JOB ID: $SLURM_JOBID"
echo "Running on nodes: $SLURM_NODELIST"
echo "------------------------------------------------------------"
 
# Load the JupyterLab module
module load palma/2021a
module load foss/2021a
module load JupyterLab/3.2.8
 
# Load every other python module you might want to use (has to be within the
# toolchain of the JupyterLab module!
module load SciPy-bundle
module load matplotlib
 
# set a random port for the notebook, in case multiple notebooks are
# on the same compute node.
NOTEBOOKPORT=`shuf -i 8000-8500 -n 1`
 
# set a random port for tunneling, in case multiple connections are happening
# on the same login node.
TUNNELPORT=`shuf -i 8501-9000 -n 1`
 
# set a random access token
TOKEN=`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 49 | head -n 1`
 
echo "On your local machine, run:"
echo ""
echo "ssh -L8888:localhost:$TUNNELPORT $USER@palma.uni-muenster.de 'ssh -L$TUNNELPORT:localhost:$NOTEBOOKPORT $SLURMD_NODENAME -N -4'"
echo ""
echo "and point your browser to http://localhost:8888/?token=$TOKEN"
echo "Change '8888' to some other value if this port is already in use on your PC,"
echo "for example, you have more than one remote notebook running."
echo "To stop this notebook, run 'scancel $SLURM_JOB_ID'"
 
# Start the notebook
srun -n1 jupyter-notebook --no-browser --port=$NOTEBOOKPORT --NotebookApp.token=$TOKEN --log-level WARN
# To stop the notebook, use 'scancel'