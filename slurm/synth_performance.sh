#!/usr/bin/bash
#SBATCH --job-name=avc-ai-testing
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --ntasks-per-node=1
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=2GB
#SBATCH --output=logs/taylora-%x-job%j.out
#SBATCH -e ERRORLOGS.out
#SBATCH --gres=gpu:0

pwd; hostname; date
export PROJECT_DIR=/home/taylora_mitre/euchre
export SCRATCH=/staging/fast/taylora
export SINGULARITY_TMPDIR=$SCRATCH

export ROOT_DIR=/staging/fast/taylora

srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 performance.py --root $ROOT_DIR --NCPUS 24 &

wait