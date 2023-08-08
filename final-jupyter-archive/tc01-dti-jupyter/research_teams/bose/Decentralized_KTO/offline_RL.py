import numpy as np
from matplotlib import pyplot as plt
import copy
#from tqdm.notebook import tqdm
import pickle
from datetime import datetime
import os
import collections

def get_iterable(x):
    if isinstance(x, collections.Iterable):
        return x
    else:
        return (x,)

def val_iter(rewards,t_matrix,theta,gamma):

    delta = theta * 10
    deltas = []
    exp_deltas = []

    n_state = np.shape(rewards)[0]
    n_action = np.shape(rewards)[1]

    val_func = np.zeros(n_state)
    val_funcs = []
    val_funcs.append(copy.deepcopy(val_func))
    #print(val_funcs[0])

    while delta>theta:
        delta = 0
        for i in range(n_state):
            v_temp = val_func[i]
            max_buffer = np.zeros(n_action)
            for j in range(n_action):
                max_buffer[j] = rewards[i][j] + gamma*np.dot(val_func,t_matrix[i][j])
            val_func[i] = np.max(max_buffer)
            delta = np.max((delta,np.abs(v_temp-val_func[i])))
        deltas.append(delta)
        val_funcs.append(copy.deepcopy(val_func))

    max_val = np.max(val_func)
    for v_func in val_funcs:
        exp_deltas.append(np.max(np.abs(val_func-v_func))/max_val)
    
    #return val_func,deltas
    return val_func,exp_deltas,np.array(val_funcs)

def q_val_iter(rewards,t_matrix,theta,gamma):

    delta = theta * 10
    deltas = []
    exp_deltas = []

    n_state = np.shape(rewards)[0]
    n_action = np.shape(rewards)[1]

    q_val_func = np.zeros((n_state,n_action))
    q_val_funcs = []
    q_val_funcs.append(copy.deepcopy(q_val_func))
    #print(val_funcs[0])

    while delta>theta:
        delta = 0
        for i in range(n_state):
            for j in range(n_action):
                q_temp = q_val_func[i][j]
                max_buffer = np.zeros(n_state)
                for k in range(n_state):
                    max_buffer[k] = np.max(q_val_func[k])
                q_val_func[i][j] = rewards[i][j] + gamma*np.dot(max_buffer,t_matrix[i][j])
                delta = np.max((delta,np.abs(q_temp-q_val_func[i][j])))
            #v_temp = val_func[i]
            #max_buffer = np.zeros(n_action)
            #for j in range(n_action):
                #max_buffer[j] = rewards[i][j] + gamma*np.dot(val_func,t_matrix[i][j])
            #val_func[i] = np.max(max_buffer)
            #delta = np.max((delta,np.abs(v_temp-val_func[i])))
        deltas.append(delta)
        #print(delta)
        q_val_funcs.append(copy.deepcopy(q_val_func))

    max_val = np.max(q_val_func)
    for q_v_func in q_val_funcs:
        exp_deltas.append(np.max(np.abs(q_val_func-q_v_func))/max_val)
    
    #return val_func,deltas
    return q_val_func,exp_deltas,np.array(q_val_funcs)

def policy_iter(rewards,t_matrix,theta,gamma):

    n_state = np.shape(rewards)[0]
    n_action = np.shape(rewards)[1]

    val_func = np.zeros(n_state)
    policy = np.zeros(n_state)

    val_old = np.zeros(np.shape(val_func))

    deltas = []
    delta = theta*10

    theta_val = 1e-10

    while delta>theta:
    #policy evaluation
        delta_val = theta_val*10
        while delta_val>theta_val:
            delta = 0
            for i in range(n_state):
                v_temp = val_func[i]
                action = int(policy[i])
                val_func[i] =rewards[i][action] + gamma*np.dot(val_func,t_matrix[i][action])
                delta_val = np.max((delta,np.abs(v_temp-val_func[i])))
    
        q_next = get_q_func(rewards=rewards,t_matrix=t_matrix,val_func=val_func,gamma=gamma)
        policy = get_policy(q_next)

        delta = np.max(np.abs(val_old-val_func))
        deltas.append(delta)
        val_old = np.copy(val_func)
    
    return val_func,policy,deltas
    
def get_q_func(rewards,t_matrix,val_func,gamma):

    n_state = np.shape(rewards)[0]
    n_action = np.shape(rewards)[1]

    q_func = np.zeros((n_state,n_action))

    for i in range(n_state):
        max_buffer = np.zeros(n_action)
        for j in range(n_action):
            max_buffer[j] = rewards[i][j] + gamma*np.dot(val_func,t_matrix[i][j])
        q_func[i] = max_buffer
        #expert_policy[i] = np.argmax(max_buffer)
    return q_func

def get_policy(q_func):

    n_state = np.shape(q_func)[0]
    policy = np.zeros(n_state)

    for i in range(n_state):
        policy[i] = np.argmax(q_func[i])

    return policy

def get_random_policy(n_action,n_state,stoch=True):

    #n_state = np.shape(q_func)[0]
    if stoch:
        policy = np.zeros((n_state,n_action))
    else:
        policy = np.zeros(n_state)

    for i in range(n_state):
        #policy[i] = np.argmax(q_func[i])
        if stoch:
            for j in range(n_action):
                policy[i][j] = 1/n_action
        else:
            policy[i] = np.random.randint(0,n_action)

    return policy

def offline_val_iter(rewards,theta,gamma,dataset,n_next_state,max_iter=1000,samp_w_replace=True):

    delta = theta * 10
    deltas = []

    #exp_scale = 1/n_next_state

    n_state = np.shape(rewards)[0]
    n_action = np.shape(rewards)[1]

    val_func = np.zeros(n_state)
    val_funcs = []
    val_funcs.append(copy.deepcopy(val_func))

    deltas = []
    #for iter in range(0,100):
    iters = 0
    while delta>theta and iters<max_iter:
        delta = 0
        for i in range(n_state):
            v_temp = val_func[i]
            max_buffer = np.zeros(n_action)
            for j in range(n_action):
                #print('i: '+str(i))
                #print('j: '+str(j))
                if len(dataset[str(i)][str(j)])==0:
                    max_buffer[j] = rewards[i][j]
                else:
                    if len(dataset[str(i)][str(j)])<n_next_state:
                        if samp_w_replace:
                            next_state_samples = np.random.choice(dataset[str(i)][str(j)],size=n_next_state)
                        else:
                            next_state_samples = dataset[str(i)][str(j)]
                    else:
                        next_state_samples = np.random.choice(dataset[str(i)][str(j)],size=n_next_state)
                    exp_scale = 1./len(next_state_samples)
                    max_buffer[j] = rewards[i][j] + gamma*exp_scale*np.sum(np.take(val_func,next_state_samples))
            val_func[i] = np.max(max_buffer)
            delta = np.max((delta,np.abs(v_temp-val_func[i])))
        deltas.append(delta)
        val_funcs.append(copy.deepcopy(val_func))
        iters+=1
    
    return val_func,deltas,val_funcs

def offline_q_val_iter(rewards,theta,gamma,dataset,n_next_state,max_iter=1000):

    delta = theta * 10
    deltas = []
    exp_deltas = []

    n_state = np.shape(rewards)[0]
    n_action = np.shape(rewards)[1]

    q_val_func = np.zeros((n_state,n_action))
    q_val_funcs = []
    q_val_funcs.append(copy.deepcopy(q_val_func))
    #print(val_funcs[0])

    exp_scale = 1/n_next_state
    iters = 0

    while delta>theta and iters<max_iter:
        delta = 0
        for i in range(n_state):
            for j in range(n_action):
                q_temp = q_val_func[i][j]
                max_buffer = np.zeros(n_state)
                for k in range(n_state):
                    max_buffer[k] = np.max(q_val_func[k])
                next_state_samples = np.random.choice(dataset[str(i)][str(j)],size=n_next_state)
                q_val_func[i][j] = rewards[i][j] + gamma*exp_scale*np.sum(np.take(max_buffer,next_state_samples))
                delta = np.max((delta,np.abs(q_temp-q_val_func[i][j])))
            #v_temp = val_func[i]
            #max_buffer = np.zeros(n_action)
            #for j in range(n_action):
                #max_buffer[j] = rewards[i][j] + gamma*np.dot(val_func,t_matrix[i][j])
            #val_func[i] = np.max(max_buffer)
            #delta = np.max((delta,np.abs(v_temp-val_func[i])))
        deltas.append(delta)
        #print(delta)
        q_val_funcs.append(copy.deepcopy(q_val_func))
        iters+=1

    return q_val_func,deltas,q_val_funcs

def offline_policy_iter(rewards,t_matrix,theta,gamma,dataset,n_next_state,n_episodes,T,max_iter=10):

    n_state = np.shape(rewards)[0]
    n_action = np.shape(rewards)[1]

    exp_scale = 1/n_next_state
    episode_scale = 1/n_episodes

    val_func = np.zeros(n_state)
    policy = np.zeros(n_state)

    deltas = []
    delta = theta*10

    policy_stable = False

    iter = 0
    while delta>theta and iter<max_iter and not policy_stable:
        print('Iteration '+str(iter))
        val_next = np.zeros(n_state)
        #print(val_func)
        for i in range(n_state):
            for q in range(n_episodes):
                #reward_steps = np.zeros(T)
                state = i
                for step in range(T):
                    action = int(policy[state])
                    val_next[i] += episode_scale*(gamma**step)*rewards[state][action]
                    #reward_steps[step] = episode_scale*(gamma**step)*rewards[state][action]
                    #print('Value: '+str(val_next[i]))
                    state = np.random.choice(dataset[str(state)][str(action)])
                    #state = np.random.choice(n_state,p=t_matrix[state][action])
                #lt.plot(reward_steps)
                #plt.savefig('Reward Steps - State '+str(i)+' Episode '+str(q)+'.png')
                #plt.close()

        plt.plot(val_next)
        plt.title('Val Next: '+str(iter))
        plt.savefig('Val Next'+str(iter)+'.png')
        plt.close()

        old_policy = np.copy(policy)
        #print('Pre Update')
        #print(old_policy)
            
        for i in range(n_state):
            max_buffer = np.zeros(n_action)
            for j in range(n_action):
                next_state_samples = np.random.choice(dataset[str(i)][str(j)],size=n_next_state)
                max_buffer[j] = rewards[i][j] + gamma*exp_scale*np.sum(np.take(val_next,next_state_samples))
            policy[i] = np.argmax(max_buffer)
        #print('Post Update')
        #print(old_policy)

        policy_stable = np.array_equal(old_policy,policy)
        print('Policy Stable: '+str(policy_stable))

        #q_next = get_q_func(rewards=rewards,t_matrix=t_matrix,val_func=val_next,gamma=gamma)
        #policy = get_policy(q_next)
        
        plt.plot(policy)
        plt.title('Policy: '+str(iter))
        plt.savefig('Policy '+str(iter)+'.png')
        plt.close()

        #print(val_func)
        delta = np.max(np.abs(val_next-val_func))
        print('Delta: '+str(delta))
        deltas.append(delta)
        val_func = np.copy(val_next)
        iter+=1
    
    return val_func,policy,deltas

def gen_dataset(policy,min_samples,t_matrix):

    n_state = np.shape(t_matrix)[0]
    n_action = np.shape(t_matrix)[1]

    s_a_done = 0
    total_s_a = n_state*n_action
    dataset = {}

    prev_state = np.random.randint(n_state)
    
    while s_a_done < total_s_a:
        action = np.random.choice(n_action,size=1,p=policy[prev_state])[0]
        state = np.random.choice(n_state,size=1,p=t_matrix[prev_state][action])
        p_state_str = str(prev_state)
        action_str = str(action)
        if p_state_str not in dataset.keys():
            dataset[p_state_str] = {}
        if action_str not in dataset[p_state_str].keys():
            dataset[p_state_str][action_str] = state
        else:
            dataset[p_state_str][action_str] = np.concatenate((dataset[p_state_str][action_str],state))
        if len(dataset[p_state_str][action_str]) == min_samples:
            s_a_done += 1
        prev_state = state[0]
        #print('Number of states covered '+str(s_a_done))


    num_samples = []
    for state_key in dataset.keys():
        for action_key in dataset[state_key].keys():
            #print('State: '+state_key+' Action: '+action_key+' Num Samples: '+str(len(dataset[state_key][action_key])))
            num_samples.append(len(dataset[state_key][action_key]))
    num_samples = np.array(num_samples)
    
    return dataset,num_samples

def gen_dataset_iterative(policy,min_samples,t_matrix,prop_covered,s_a_string):

    date = datetime.now().strftime("%Y_%m_%d_%M_%S")

    n_state = np.shape(t_matrix)[0]
    n_action = np.shape(t_matrix)[1]

    dataset = {}
    total_s_a = int(n_state*n_action*prop_covered)
    prev_state = np.random.randint(n_state)

    min_samples = get_iterable(min_samples)

    for i in range(n_state):
        dataset[str(i)] = {}
        for j in range(n_action):
            dataset[str(i)][str(j)] = {}

    for min_s in min_samples:

        print('Generating data up to '+str(min_s)+' for '+str(prop_covered*100)+'% of (s,a) Pairs')

        s_a_done = np.zeros((n_state,n_action))
        #total_s_a = n_state*n_action        
        while np.sum(s_a_done) < total_s_a:
            action = np.random.choice(n_action,size=1,p=policy[prev_state])[0]
            state = np.random.choice(n_state,size=1,p=t_matrix[prev_state][action])
            p_state_str = str(prev_state)
            action_str = str(action)
            #if p_state_str not in dataset.keys():
            #    dataset[p_state_str] = {}
            #if action_str not in dataset[p_state_str].keys():
            #    dataset[p_state_str][action_str] = state
            if len(dataset[p_state_str][action_str])==0:
                dataset[p_state_str][action_str] = state
            else:
                dataset[p_state_str][action_str] = np.concatenate((dataset[p_state_str][action_str],state))
            if len(dataset[p_state_str][action_str]) >= min_s:
                #s_a_done += 1
                s_a_done[prev_state][action] = 1
            prev_state = state[0]
            #print('Number of states covered '+str(np.sum(s_a_done)))
        
        with open(os.path.join('Datasets',s_a_string+'_min_samp_'+str(min_s)+'_'+date+'.pkl'),'wb') as f:
            pickle.dump(dataset,f)
    
    return dataset