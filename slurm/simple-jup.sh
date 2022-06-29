#!/usr/bin/bash
#SBATCH --job-name=jupyter-cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --ntasks-per-node=1
#SBATCH --time=36:00:00
#SBATCH --mem=32GB
#SBATCH --output=slurm/logs/taylora-%x-job%j.out
#SBATCH --gres=gpu:0

pwd; hostname; date

export PROJECT_DIR=/home/taylora_mitre/
export QDIR=/q/
export SCRATCH=/staging/
export SINGULARITY_TMPDIR=$SCRATCH

srun singularity exec --nv --bind $QDIR,$PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/ray_nvidia.sif jupyter-lab \
        --ip=* --port=5035 --allow-root --notebook-dir=$PROJECT_DIR
