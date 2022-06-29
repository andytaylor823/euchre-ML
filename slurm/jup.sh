#!/usr/bin/bash
#SBATCH --job-name=jeupyter-gpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --ntasks-per-node=1
#SBATCH --time=36:00:00
#SBATCH --mem-per-cpu=36GB
#SBATCH --output=euchre/logs/taylora-%x-job%j.out
#SBATCH --gres=gpu:1

pwd; hostname; date

export PROJECT_DIR=/home/taylora_mitre/
export SCRATCH=/staging/fast/taylora
export SINGULARITY_TMPDIR=$SCRATCH
export SINGULARITYENV_APPEND_PATH="/home/taylora_mitre/.nvm/versions/node/v16.0.0/bin/"

srun singularity exec --nv --bind $PROJECT_DIR,$SCRATCH,/q/ /q/AVC-AI/taylora/tensorflow.sif jupyter-lab \
	--ip=* --port=8898 --allow-root --notebook-dir=$PROJECT_DIR

#srun singularity exec --nv --bind $PROJECT_DIR,$SCRATCH,/q/ /home/taylora_mitre/tensorflow_alt.sif jupyter-lab \
#       --ip=* --port=8898 --allow-root --notebook-dir=$PROJECT_DIR

#srun singularity exec --nv \
#         --bind /q:/q $PROJECT_DIR/tensorflow.sif \
#        #--bind $PROJECT_DIR, $SCRATCH $PROJECT_DIR/tensorflow.sif \
#        #tensorflow.sif
#	jupyter lab --ip=0.0.0.0 --port=8899 --allow-root \
#        --notebook-dir $PROJECT_DIR
