#!/bin/bash


if [ $# -ne 4 ]; then
  echo "fetch_results.sh <puhti|mahti> <num-last-csv-logs> <experiment-dir>"
  echo " e.g fetch_results.sh puhti 40 1 exp-20-rwd-z.invtime-2x32-lr0.001-30k-10mu-minus0.5logstd"
  exit 1;
fi

base_logdir="/scratch/project_*/velcontrol-rl-keller/runvpg/"

server=$1
num_last_csv_logs=$2
num_last_models=$3
exp_dir=$4

mkdir -p $exp_dir $exp_dir/csv $exp_dir/${exp_dir}_s0

echo $exp_dir
rsync -r --exclude '*.pkl' --exclude '*.pt' $server:/${base_logdir}/$exp_dir/${exp_dir}_s0/ $exp_dir/${exp_dir}_s0/
scp $server:/${base_logdir}/$exp_dir/exp_parameters.txt $exp_dir/

track_length=$(grep "track_length" $exp_dir/exp_parameters.txt | cut -d ':' -f 2)
echo $track_length

python vpg_plot_train_history.py $exp_dir/${exp_dir}_s0
# python vpg_run_model.py $exp_dir/${exp_dir}_s0/pyt_save/model.pt --num-episodes 5 --log-raw-csv

ssh $server "ls /${base_logdir}/$exp_dir/csv | sort -t "_" -k 2 -n -r | head -n $num_last_csv_logs" | \
	while read line; do
		if [ ! -f $exp_dir/csv/$line ]; then
			scp $server:/${base_logdir}/$exp_dir/csv/$line $exp_dir/csv/;
		fi 
	done;
python turn_csv_to_fig.py --plot-kellers --plot-kellers-track-length $track_length --num-last-files $num_last_csv_logs $exp_dir


ssh $server "ls /${base_logdir}/$exp_dir/${exp_dir}_s0/pyt_save | sed 's/model//g' | sed 's/.pt//g' | sort -n -r | head -n $num_last_models" | \
	while read line; do
		file="/${base_logdir}/$exp_dir/${exp_dir}_s0/pyt_save/model${line}.pt"
		if [ ! -f $file ]; then
			scp $server:$file $exp_dir/${exp_dir}_s0/pyt_save/;
		fi 
	done;

./run_all_models.sh $exp_dir/${exp_dir}_s0/pyt_save/ $track_length