#!/bin/bash
#SBATCH --job-name=optimalcontrol
#SBATCH --account=Project_2007094
#SBATCH --partition=longrun
#SBATCH --time=14-00:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem-per-cpu=2G

module load pytorch/1.13 gcc/9.4.0 openmpi/4.1.4

if [ $# -ne 8 ]; then
  echo "batch_single_vpg.sh <experiment-number> <experiment-info> <hidden-sizes> \
  							<lr> <epochs> <track-length> \
							<batch-size> <delta-time>"
  echo " e.g batch_single_vpg.sh 9 smallcapacity-longtrack 32,32 0.001 500 1000 5000 0.1"
  exit 1;
fi

base_logdir="/scratch/project_2007094/velcontrol-rl-keller/runvpg/"


exp_num=$1
exp_info=$2
hidden_sizes=$3
lr=$4
epochs=$5
track_length=$6
batch_size=$7
delta_time=$8

bash -x ./batch_single_vpg_general.sh $exp_num $exp_info $hidden_sizes \
								$lr $epochs $track_length \
								$batch_size $delta_time \
								$base_logdir

