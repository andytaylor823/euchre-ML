#!/usr/bin/bash
#SBATCH --job-name=avc-ai-testing
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=24
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=2GB
#SBATCH --output=logs/taylora-%x-job%j.out
#SBATCH -e ERRORLOGS.out
#SBATCH --gres=gpu:0

pwd; hostname; date
rm ERRORLOGS.out
export PROJECT_DIR=/home/taylora_mitre/euchre
export SCRATCH=/staging/fast/taylora
export SINGULARITY_TMPDIR=$SCRATCH

export NEPOCHS=1000
export NHANDS=10000
export TQDM=1
export ROOT_DIR=/staging/fast/taylora

srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  70 --tqdm $TQDM --id 1 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  71 --tqdm $TQDM --id 2 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  72 --tqdm $TQDM --id 3 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  73 --tqdm $TQDM --id 4 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  74 --tqdm $TQDM --id 5 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  75 --tqdm $TQDM --id 6 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  76 --tqdm $TQDM --id 7 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  77 --tqdm $TQDM --id 8 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  78 --tqdm $TQDM --id 9 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  79 --tqdm $TQDM --id 10 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  80 --tqdm $TQDM --id 11 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  81 --tqdm $TQDM --id 12 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  82 --tqdm $TQDM --id 13 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  83 --tqdm $TQDM --id 14 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  84 --tqdm $TQDM --id 15 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  85 --tqdm $TQDM --id 16 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  86 --tqdm $TQDM --id 17 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  87 --tqdm $TQDM --id 18 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  88 --tqdm $TQDM --id 19 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  89 --tqdm $TQDM --id 20 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  90 --tqdm $TQDM --id 21 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  91 --tqdm $TQDM --id 22 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  92 --tqdm $TQDM --id 23 &
srun --nodes 1 singularity exec --nv --bind $PROJECT_DIR,$SCRATCH /q/AVC-AI/taylora/tensorflow.sif python3 play_hands.py --ne $NEPOCHS --nh $NHANDS --root $ROOT_DIR --rmdir 1 --thresh  93 --tqdm $TQDM --id 24 &

wait
#srun singularity exec --nv --bind $PROJECT_DIR,$SCRATCH $PROJECT_DIR/taylora/tensorflow.sif jupyter-lab \
#        --ip=* --port=8899 --allow-root --notebook-dir=$PROJECT_DI