import numpy as np
import gym

from scipy.spatial.distance import pdist, squareform, cdist

import h5py

max_speed = 8

with h5py.File('pendulum_model_CME.h5', 'r') as hf:
# with h5py.File('pendulum_model_300s_100a.h5', 'r') as hf:
    # g = hf["g"]
    actions = hf["actions"][:]
    # xy = hf["xy"][:]
    xy_norm = hf["xy_norm"][:]
    policy = hf["CME_grid_policy"][:]
    # VI_val_fcn = hf["VI_val_fcn"][:]

g = 10.0

env =  gym.make('Pendulum-v1', g=g)
obs = env.reset()

state = env.state

while True:

    dists = cdist(xy_norm,np.reshape([state[0]/np.pi,state[1]/max_speed],(1,-1)),metric='sqeuclidean')
    # dists = cdist(xy,np.reshape([state[0],state[1]],(1,-1)),metric='euclidean')
    state_q_ind = int(np.argmin(dists))
    action = actions[int(policy[state_q_ind])]

    env.render()

    next_state, reward, done, _ = env.step(action[np.newaxis])
    state = env.state
    
    if done:
        # if state[0]>=0.5:
        #     print('Success!')
        break

env.close()