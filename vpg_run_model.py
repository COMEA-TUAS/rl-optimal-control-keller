from genericpath import exists
import torch
from datetime import datetime as dt
import os
import sys
from functools import cmp_to_key
import environment_gym
from shutil import copyfile

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-path', type=str)    
    parser.add_argument('--log-dir', type=str, default=None)
    parser.add_argument('--num-episodes', type=int, default=1)
    parser.add_argument('--log-raw-csv', action='store_true')
    parser.add_argument('--track-length', type=float, default=100)
    parser.add_argument('--time-limit', type=float, default=20)
    parser.add_argument('--all-figs-dir', type=str, default=None)
    args = parser.parse_args()
    
    # print(" ".join(sys.argv))
    print(args)



    if os.path.isdir(args.model_path):
        print("shit")
        models_dir = args.model_path
        model_files = [x for x in os.listdir(models_dir) if x.endswith(".pt")]
    else:
        models_dir = os.path.dirname(args.model_path)
        model_files = [os.path.basename(args.model_path)]

    base_log_dir = args.log_dir
    if base_log_dir is None:
        base_log_dir = os.path.join(models_dir, "log-{}".format(dt.now().strftime("%Y-%m-%d_%H-%M-%S")))

    model_files = sorted(model_files, 
                    key=cmp_to_key(lambda y, x: int(x.split("l")[1].split(".")[0]) - int(y.split("l")[1].split(".")[0])),
                    reverse=False
                )

    if args.all_figs_dir is not None:
            os.makedirs(args.all_figs_dir, exist_ok=True)
    print(model_files)
    for i, model_file in enumerate(model_files):
        print("{}/{}: {}".format(i, len(model_files), model_file))
        log_dir = os.path.join(base_log_dir, os.path.basename(model_file))
        if os.path.exists(os.path.join(log_dir, "fig")):
            continue
        env = environment_gym.Env(log_dir=log_dir, 
                            track_length=args.track_length,
                            time_limit=args.time_limit, delta_time=0.1)
        # env.enable_log_raw_csv(1)
        
        csv_log_dir = os.path.join(log_dir, "csv")
        os.makedirs(csv_log_dir, exist_ok=True)
        
        # ac = MLPActorCritic(env.observation_space, env.action_space, [32])
        # ac = ac.load_state_dict(torch.load(args.model_path))
        
        ac = torch.load(os.path.join(models_dir, model_file))
            
        for i in range(args.num_episodes):  
            log_file = os.path.join(csv_log_dir, f"log_{i}.csv")
            csv_log_file = open(log_file, mode="w")

            done = False
            state = env.reset()
            print("time,x,velocity,E,propulsion_force,acceleration,reward,stddev", file=csv_log_file)
            print(",".join(["\""+str(x)+"\"" for x in
                ([env.time] + list(state) + [0, env.object.acceleration, 0, 0])
            ]), file=csv_log_file)

            while True:
                # action, _, _ = ac.step(torch.as_tensor(state, dtype=torch.float32)) # Categorical(logits=logits).sample().item()
                obs = torch.as_tensor(state, dtype=torch.float32)
                net_out = ac.pi.net(obs)
                action = ac.pi._distribution(obs).mean
                var_std = ac.pi._distribution(obs).stddev 
                # ac.step() # Categorical(logits=logits).sample().item()
                state, reward, done, succ = env.step(action.detach().numpy())
                print(",".join([f"\"{x:.4f}\"" for x in
                    [env.time] + list(state) + [action.detach().item(), env.object.acceleration, 
                    reward, var_std.detach().item()] 
                ]), file=csv_log_file) 
                if done:
                    with open(os.path.join(csv_log_dir, f"log_{i}_info.txt"), mode="w") as f:
                        print(env.done_reason, file=f)
                    state = env.reset()
                    break

                # print(obs, net_out, var_std)
        csv_log_file.flush()
        csv_log_file.close()
        from turn_csv_to_fig import turn_csv_to_fig
        turn_csv_to_fig(log_dir, num_last_files=1)

        if args.all_figs_dir is not None:
            fig_dir = os.path.join(log_dir, "fig")
            for src_fig_name in os.listdir(fig_dir):
                copyfile(os.path.join(fig_dir, src_fig_name), os.path.join(args.all_figs_dir, "{}_{}".format(model_file, src_fig_name)))
