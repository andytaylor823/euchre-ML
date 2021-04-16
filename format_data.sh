#!/usr/bin/bash
#SBATCH --job-name=format-data
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=25:00:00
#SBATCH --mem-per-cpu=2GB
#SBATCH --output=logs/taylora-%x-job%j.out
#SBATCH --gres=gpu:0

pwd; hostname; date

export PROJECT_DIR=/q/
export SCRATCH=/staging/fast/taylora
export SINGULARITY_TMPDIR=$SCRATCH

srun singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 -u format_to_tfrecord.py