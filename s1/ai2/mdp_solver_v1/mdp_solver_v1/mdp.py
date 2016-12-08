# Basic functions for MDP planning and learning
# Luca Iocchi 2015

import sys
import random
 
# Domain independent functions

def valueIteration(states, actions, transition_function, reward_function, gamma=0.9, iterations=10, set_final_states=set()):
    if isinstance(set_final_states, set):
        set_final_states = set(set_final_states)

    V={x:0 for x in states}
    
    for i in range(iterations):
        print("\nIteration ", i)
        Vn = V.copy() # clone
        for current_state in states: # current state
            if current_state in set_final_states:
                continue

            #print "\tCurrent state ",current_state
            maxVa =- 1
            for action in actions:
                #print "\t\tAction ",actiona
                sumx=0
                for next_state in states: # next state
                    #print "\t\t\tSuccessor state ",next_state," prob: ",P(current_state,action,next_state)
                    sumx += transition_function(current_state, action, next_state) * (reward_function(current_state, action, next_state) + gamma * V[next_state])
                maxVa = max(sumx,maxVa)
            Vn[current_state] = maxVa
        V = Vn
        print(("V  = ",V))
        #print "pi = ",optimalPolicy(V)
    return V

# compute optimal policy from the value function V
def optimalPolicyV(V,X,A,P,r,gamma=0.9):
    pi = {}
    bestA = []  # set of best actions
    for x1 in X:
        maxVa=-1
        for a in A:
            sumx=0
            for x2 in X: # next state
                sumx += P(x1,a,x2) * (r(x1,a,x2) + gamma * V[x2])

            if sumx>maxVa:
               maxVa = sumx
               bestA = [a]
            elif sumx==maxVa:
               bestA.append(a)
        pi[x1] = random.choice(bestA) # choose one among the best actions for state x
    return pi


def getQ(Q,x,a):
    try:
        return Q[(x,a)]
    except KeyError:
        return 0
      
# deterministic Q update
def updateQdet(Q_new,Q,A,x1,a,x2,r,gamma):
    assert A
    maxQ=-1
    for a2 in A:
        maxQ=max(getQ(Q,x2,a2),maxQ)
    Q_new[(x1,a)] = r + gamma * maxQ

# non-deterministic Q update 
def updateQ(Q_new,Q,A,x1,a,x2,r,gamma,alpha):
    assert A
    maxQ=-1
    for a2 in A:
        maxQ=max(getQ(Q,x2,a2),maxQ)
    Q_new[(x1,a)] = getQ(Q,x1,a) + alpha * (r + gamma*maxQ - getQ(Q,x1,a))

def argmaxQa(Q,x,A):
    maxQ=-1
    bestA=[]
    for a in A:
        q = getQ(Q,x,a)
        if q>maxQ:
            maxQ = q
            bestA = [a] # set of best actions for state x
        elif q==maxQ:   
            bestA.append(a)
    return random.choice(bestA)

def chooseA(Q,x,A,epsilon):
    # epsilon greedy
    a=A[0]
    if random.random()<epsilon:
        a = random.choice(A)
        print("ExploRAtion")
    else:        
        a = argmaxQa(Q,x,A)
        print("ExploITation")
    return a

    
# x0: initial state
# Sxf: set of final states
# A: set of actions
# delta_exec(x,a): execution function to observe the successor state 
#                  of executing a from x
# reward_exec(x,a): reward function to observe the reward obtained  
#                   by executing a from x
# gamma: discount factor
# epsilon: value for epsilon-greedy strategy
# alpha: value for non-deterministic update rule
# iterations: number of iterations of the algorithm
# RR: [output] cumulative reward obtained over iterations
# NA: [output] total number of actions executed 
def Qlearning(x0,set_final_states,A,delta_exec,reward_exec,gamma,epsilon,alpha,iterations,RR,NA):
    Q = {}
    x = x0
    NA[0] = 0
    for i in range(iterations):
        Qn = dict(Q)
        print(("\nIteration ",i))
        x = x0 # set current state as initial state
        g = 1.0 # discount
        rr = 0.0 # cumulative reward
        while x and x not in set_final_states:
            a = chooseA(Q,x,A,epsilon)
            # Execution of action a in state x
            print(" - Execution: state ",x," action ",a)
            NA[0] = NA[0] + 1
            x2 = delta_exec(x,a)
            r = reward_exec(x,a,x2)
            rr = rr + r * g
            g = g * gamma
            print(" -   outcome: state ",x2," reward ",r)
            if x2==-1:
                break
            updateQ(Qn,Q,A,x,a,x2,r,gamma,alpha)
            x = x2
        Q = Qn
        RR[i] = rr
        print(("Cumulative reward: ",rr))
        print("\n")
    return Q


# Compute the optimal policy from the Q function
def optimalPolicyQ(Q,X,A):
    pi = {}
    for x in X:
        # set best action for state x
        pi[x] = argmaxQa(Q,x,A)
    return pi

    
# Execute policy pi from x0 to Sxf, print execution trace and cumulative reward
def execTrace(x0,xg,Sxf,delta,r,gamma,pi):
    print(("Execution trace from ",x0))
    i=0
    x=x0
    g = 1.0
    rr = 0.0 # cumulative reward
    while not x in Sxf:
        a = pi[x]
        i=i+1
        x2 = delta(x,a)
        r2 = r(x,a,x2)
        print((i,":  ",x,a,"->",x2," ",r2))
        rr = rr + r2*g
        g = g*gamma
        x = x2
        if isinstance(x, int) and x<0:
            print("Execution Error")
            return
        if not x:
            print("Execution Error (edited)")
            return
        if (i==10):
            print("LOOP")
            return
    if x==xg:
        print("GOAL")
    else:
        print("FAIL")
    print(("Cumulative reward = ",rr))
