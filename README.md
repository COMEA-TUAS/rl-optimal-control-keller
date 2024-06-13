# RL solution for optimal pacing profile
This repository is the implementation of paper

Shahsavari, S., Immonen, E., Karami, M., Haghbayan, M.H. and Plosila, J., 2022. How To Run A World Record? A Reinforcement Learning Approach. In ECMS (pp. 159-166).

The code include a simulation model implemented in Gym environment standard, as well as built-in devised reward function and the reinforcement learning approach to maximize the cumulative reward. The output of this optimization is then the force profile that the runner should apply during the course of the fixed-length track to achieve minimum time. 

The implementation is compatible with CSC super computer architecture and includes Slurm batch files (see batch_single_vpg_puhti.sh for example).  

