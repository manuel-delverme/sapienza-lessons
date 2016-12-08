# MDP for simple grid example
# Luca Iocchi 2015

import sys

import mdp
from mdp import *

# MDP definition for simple deterministic grid world

X = ['S0', 'S1', 'S2', 'S3', 'S4', 'G']
A = ['R', 'L', 'U', 'D']

deltaS = { ('S0','R'): 'S1',  ('S0','U'): 'S3',
           ('S1','R'): 'S2',  ('S1','L'): 'S0',  ('S1','U'): 'S4',
           ('S2','L'): 'S1',  ('S2','U'): 'G',
           ('S3','R'): 'S4',  ('S3','D'): 'S0',
           ('S4','R'): 'G',   ('S4','L'): 'S3',  ('S3','D'): 'S0'
        }

reward = { 'G': 100 }

x0 = X[0] # initial state
xg = X[5] # goal state
Sxf = [X[5]] # set of final states

def delta(x, a):
    if (x,a) in deltaS:
        return deltaS[(x,a)]
    else:
        return None

def delta_exec(x, a):
    return delta(x,a)

def P(x1,a,x2): # transition probability    
    if (delta(x1,a) == x2):
        return 1
    else:
        return 0

        
def r(x1,a,x2): # reward value
    if (x2 in reward):
        return reward[x2]
    else:
        return 0


        
# main
# Options: [Planning/Learning] [niterations] [epsilon]

niter=10
gamma=0.9
epsilon=0.5
alpha=1.0
mode='Planning'
if len(sys.argv) > 1:
   mode=sys.argv[1]
if len(sys.argv) > 2:
   niter=int(sys.argv[2])
if len(sys.argv) > 3:
    epsilon=float(sys.argv[3])

if mode=='Planning':
    V = valueIteration(X,A,P,r,gamma,niter,Sxf)
    pi = optimalPolicyV(V,X,A,P,r,gamma)
    print(("Optimal policy: ",pi))
    execTrace(x0,xg,Sxf,delta_exec,r,gamma,pi)
else:
    RR = list(range(niter))
    NA = [0]
    Q = Qlearning(x0,xg,A,delta,r,gamma,epsilon,alpha,niter,RR,NA)
    print("Q = ",Q)
    pi = optimalPolicyQ(Q,X,A)
    print("Cumulative reward = ",RR)
    print("Total action executed = ",NA[0])
    print("Optimal policy: ",pi)
    execTrace(x0,xg,Sxf,delta_exec,r,gamma,pi)
