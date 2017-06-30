# Introduction (goal of the project)
Artificial Intelligence research and games create a mutually beneficial relationship. Games on the one
hand, are commonly used for entertainment whereas Artificial Intelligence can be applied to multiple
domains, not only games. As games are mostly well-defined and small environments, they provide a
great area for research of Artifical Intelligence because solutions can be be adapted to other domains like
stock-market-trading or automated controlling of machines. The general question, either for games or
related categories like controlling problems, is which action a decision maker should choose at a given
time in order to maximize his performance in the environment.
A common model for this decision making problem are Markov Decision Processes (MDPs) which represent
the problem as a formal structure of states, actions and transitions between states, leading to a
reward. They can be solved or approximated using methods of Dynamic Programming (DP) or reinforcement
learning. Both approaches can be used to find an optimal or nearby optimal solution which allows
the decision maker to maximize his reward in the MDP.
Instead of learning from a set of predefined input-output pairs with expected input and output, as used
by supervised learning, reinforcement learning uses the agent’s interaction with the environment to learn
more or less rewarding actions. Exact solutions to a MDP decision problem are not always possible,
especially for environments with a large space of possible states and actions. For this reason approximate
methods are used, which reduce the size of the search space while still maintaining a good performance
if chosen well.
A game with such a large space and complex state representations is Hearthstone: Heroes of Warcraft
where the decision problem has been solved quite well using a Monte Carlo tree search [1]. One disadvantage
of this approach is the inability to re-use observed informations between different matches,
therefore the Monte Carlo approach is feasible when evaluating but unable to learn from it’s observations.
This work focuses on the elaboration of an approximating policy for Hearthstone, which will be learned
using reinforcement learning algorithms. We search for a value function which is capable to estimate
the “quality” of a game state. By exploiting this value function, the decision making agent could select a
valuable action by only evaluation the direct next state, instead of using deep rollouts like a Monte Carlo
tree search.

# Description of the problem

The goal of this thesis is to develop an approximating policy for the game Hearthstone via reinforcement
learning which can be used by an agent to play the game. This requires an approximate value function to
score states of the game as the entire state space of Hearthstone is too large for an exact representation.
We investigate the upcoming difficulties which emerge when designing an approximate feature set for
a complex environment. We evaluate how such an approximation can be optimized and how well it
performs when compared against other state-of-the-art solutions.

# Formal model of the problem

We already introduced the general topic of this thesis in Section 1 and defined our goal in Section 1.1. In
this section, we give an overview over the overall structure and a short insight in each of the following
seven sections.
After this introduction, we present a deeper introduction to the reinforcement learning topic in Section 2.
We use the formal model of a Markov decision process in Section 2.2 to formalize the general learning
problem. Section 2.3 introduces the policy iteration process as abstract model to generate a series of improving
policies, followed by Section 2.4 where we have a deeper look at the exploration vs exploitation
dilemma.
5
Algorithms for reinforcement learning are introduced in Section 2.5, starting with the class of TD algorithms
as general approach to reinforcement learning problems. A more advanced approach for policy
iteration is then shown in Section 2.6, where we have a deeper look at the Least Squares Policy Iteration
algorithm. In the same context, we have a look at approaches to reduce the amount of required training
samples, namely importance sampling in Section 2.7 as approach to re-use samples from different probability
distributions and gradient based policy updates in Section 2.8 to modify the update rate of learned
weights.
After we summarized the reinforcement learning techniques for our further works, we use Section 3 to
introduce the game Hearthstone as problem domain for our work. We have a deeper look at the game
mechanics and define the logic entities and properties in the game’s domain.
Our main work starts in Section 4, where we use the definitions and algorithms of Section 2 and the domain
knowledge from Section 3 to apply reinforcement learning to Hearthstone. Therefore, we introduce
the action space for a Hearthstone agent in Section 4.1 and have a deeper look at the complexity of action
sequences. In order to handle the large state space of the game, we develop features for Hearthstone
game properties to receive an approximating value function in Section 4.2. We will also discuss further
problems like randomness in Section 4.4 or the decision when to end the turn in Section 4.5. Finally
describe our learning approach for Hearthstone with different setups in Section 4.7.
We evaluate our approach in Section 5 where we test the solutions from the previous section in different
experiments. These experiments are based on a Hearthstone simulation framework for Monte Carlo
tree search algorithms, which we describe in Section 5.1. We implement policies for different agents in
Section 5.3. The impact of different learning parameters on the trained agent’s performance is then
evaluated in Section 5.4, Section 5.5 and Section 5.6.
In Section 5.7 we test our approximation features for a game state and evaluate the required sample size
to train them. After all these experiments, we summarize our results in Section 5.10 where we test the
best agents from the previous experiments against each other in a round robin tournament.
After our experiments, we compare our work to related projects in Section 6 while focusing on differences
and similarities to them.
Last but not least, we conclude our work in Section 7, where we summarize our overall results and the
experienced issues and solutions.
Ideas which were out-of-scope of this thesis but valuable for future work are explained in Section 8.



# Solution algorithm

== Algorithm ==
The problem model consists of an agent, states {{tmath|S}} and a set of actions per state {{tmath|A}}. By performing an action <math>a \in A</math>, the agent can move from state to state. Executing an action in a specific state provides the agent with a reward (a numerical score). The goal of the agent is to maximize its total reward. It does this by learning which action is optimal for each state. The action that is optimal for each state is the action that has the highest long-term reward. This reward is a weighted sum of the [[expected value]]s of the rewards of all future steps starting from the current state, where the weight for a step from a state <math>\Delta t</math> steps into the future is calculated as <math>\gamma^{\Delta t}</math>. Here, <math>\gamma</math> is a number between 0 and 1 (<math>0 \le \gamma \le 1</math>) called the discount factor and trades off the importance of sooner versus later rewards. <math> \gamma </math> may also be interpreted as the likelihood to succeed (or survive) at every step <math>\Delta t</math>.

The algorithm therefore has a function that calculates the Quantity of a state-action combination:

:<math>Q: S \times A \to \mathbb{R}</math>

Before learning has started, {{tmath|Q}} returns an (arbitrary) fixed value, chosen by the designer. Then, each time the agent selects an action, and observes a reward and a new state that may depend on both the previous state and the selected action, <math>Q</math> is updated. The core of the algorithm is a simple [[Markov decision process#Value iteration|value iteration update]]. It assumes the old value and makes a correction based on the new information.

:<math>Q(s_{t},a_{t}) \leftarrow \underbrace{Q(s_{t},a_{t})}_{\rm old~value} + \underbrace{\alpha_{t}}_{\rm learning~rate} \cdot \left( \overbrace{\underbrace{r_{t+1}}_{\rm reward} + \underbrace{\gamma}_{\rm discount~factor} \cdot \underbrace{\max_{a}Q(s_{t+1}, a)}_{\rm estimate~of~optimal~future~value}}^{\rm learned~value} - \underbrace{Q(s_{t},a_{t})}_{\rm old~value} \right)</math>

where ''<math>r_{t+1}</math>'' is the reward observed after performing <math>a_{t}</math> in <math>s_{t}</math>, and where <math>\alpha_{t}</math> is the learning rate (<math>0 < \alpha_{t} \le 1</math>).

An episode of the algorithm ends when state <math>s_{t+1}</math> is a final state (or, "absorbing state"). However, ''Q''-learning can also learn in non-episodic tasks. If the discount factor is lower than 1, the action values are finite even if the problem can contain infinite loops.

Note that for all final states <math>s_f</math>, <math>Q(s_f, a)</math> is never updated but is set to the reward value <math>r</math>. In most cases, <math>Q(s_f,a)</math> can be taken to be equal to zero.


# Implementation

Learning rate[edit]
The learning rate or step size determines to what extent the newly acquired information will override the old information. A factor of 0 will make the agent not learn anything, while a factor of 1 would make the agent consider only the most recent information. In fully deterministic environments, a learning rate of {\displaystyle \alpha _{t}=1} {\displaystyle \alpha _{t}=1} is optimal. When the problem is stochastic, the algorithm still converges under some technical conditions on the learning rate that require it to decrease to zero. In practice, often a constant learning rate is used, such as {\displaystyle \alpha _{t}=0.1} {\displaystyle \alpha _{t}=0.1} for all {\displaystyle t} t.[1]

Discount factor[edit]
The discount factor {\displaystyle \gamma } \gamma  determines the importance of future rewards. A factor of 0 will make the agent "myopic" (or short-sighted) by only considering current rewards, while a factor approaching 1 will make it strive for a long-term high reward. If the discount factor meets or exceeds 1, the action values may diverge. For {\displaystyle \gamma =1} \gamma =1, without a terminal state, or if the agent never reaches one, all environment histories will be infinitely long, and utilities with additive, undiscounted rewards will generally be infinite.[2] Even with a discount factor only slightly lower than 1, the Q-function learning leads to propagation of errors and instabilities when the value function is approximated with an artificial neural network.[3] In that case, it is known that starting with a lower discount factor and increasing it towards its final value yields accelerated learning.[4]

Initial conditions (Q0)[edit]
Since Q-learning is an iterative algorithm, it implicitly assumes an initial condition before the first update occurs. High initial values, also known as "optimistic initial conditions",[5] can encourage exploration: no matter what action is selected, the update rule will cause it to have lower values than the other alternative, thus increasing their choice probability. Recently, it was suggested that the first reward {\displaystyle r} r could be used to reset the initial conditions.[citation needed] According to this idea, the first time an action is taken the reward is used to set the value of {\displaystyle Q} Q. This will allow immediate learning in case of fixed deterministic rewards. Surprisingly, this resetting-of-initial-conditions (RIC) approach seems to be consistent with human behaviour in repeated binary choice experiments.[6]

Implementation[edit]
Q-learning at its simplest uses tables to store data. This very quickly loses viability with increasing sizes of state/action space of the system it is monitoring/controlling. One answer to this problem is to use an (adapted) artificial neural network as a function approximator, as demonstrated by Tesauro in his Backgammon playing temporal difference learning research.[7]

More generally, Q-learning can be combined with function approximation.[8] This makes it possible to apply the algorithm to larger problems, even when the state space is continuous, and therefore infinitely large. Additionally, it may speed up learning in finite problems, due to the fact that the algorithm can generalize earlier experiences to previously unseen states.

For this tutorial in my Reinforcement Learning series, we are going to be exploring a family of RL algorithms called Q-Learning algorithms. These are a little different than the policy-based algorithms that will be looked at in the the following tutorials (Parts 1–3). Instead of starting with a complex and unwieldy deep neural network, we will begin by implementing a simple lookup-table version of the algorithm, and then show how to implement a neural-network equivalent using Tensorflow. Given that we are going back to basics, it may be best to think of this as Part-0 of the series. It will hopefully give an intuition into what is really happening in Q-Learning that we can then build on going forward when we eventually combine the policy gradient and Q-learning approaches to build state-of-the-art RL agents (If you are more interested in Policy Networks, or already have a grasp on Q-Learning, feel free to start the tutorial series here instead).
Unlike policy gradient methods, which attempt to learn functions which directly map an observation to an action, Q-Learning attempts to learn the value of being in a given state, and taking a specific action there. While both approaches ultimately allow us to take intelligent actions given a situation, the means of getting to that action differ significantly. You may have heard about DeepQ-Networks which can play Atari Games. These are really just larger and more complex implementations of the Q-Learning algorithm we are going to discuss here.
Tabular Approaches for Tabular Environments

The rules of the FrozenLake environment.
For this tutorial we are going to be attempting to solve the FrozenLake environment from the OpenAI gym. For those unfamiliar, the OpenAI gym provides an easy way for people to experiment with their learning agents in an array of provided toy games. The FrozenLake environment consists of a 4x4 grid of blocks, each one either being the start block, the goal block, a safe frozen block, or a dangerous hole. The objective is to have an agent learn to navigate from the start to the goal without moving onto a hole. At any given time the agent can choose to move either up, down, left, or right. The catch is that there is a wind which occasionally blows the agent onto a space they didn’t choose. As such, perfect performance every time is impossible, but learning to avoid the holes and reach the goal are certainly still doable. The reward at every step is 0, except for entering the goal, which provides a reward of 1. Thus, we will need an algorithm that learns long-term expected rewards. This is exactly what Q-Learning is designed to provide.
In it’s simplest implementation, Q-Learning is a table of values for every state (row) and action (column) possible in the environment. Within each cell of the table, we learn a value for how good it is to take a given action within a given state. In the case of the FrozenLake environment, we have 16 possible states (one for each block), and 4 possible actions (the four directions of movement), giving us a 16x4 table of Q-values. We start by initializing the table to be uniform (all zeros), and then as we observe the rewards we obtain for various actions, we update the table accordingly.
We make updates to our Q-table using something called the Bellman equation, which states that the expected long-term reward for a given action is equal to the immediate reward from the current action combined with the expected reward from the best future action taken at the following state. In this way, we reuse our own Q-table when estimating how to update our table for future actions! In equation form, the rule looks like this:
Eq 1. Q(s,a) = r + γ(max(Q(s’,a’))
This says that the Q-value for a given state (s) and action (a) should represent the current reward (r) plus the maximum discounted (γ) future reward expected according to our own table for the next state (s’) we would end up in. The discount variable allows us to decide how important the possible future rewards are compared to the present reward. By updating in this way, the table slowly begins to obtain accurate measures of the expected future reward for a given action in a given state. Below is a Python walkthrough of the Q-Table algorithm implemented in the FrozenLake environment:


# Data structures
# Main implementation details
# Experimental evaluation

plotsss


# Use cases
# Comparative solutions
# Presentation of the results
# Discussion of the results
# Conclusions (possible future work)


Q-Learning with Neural Networks
Now, you may be thinking: tables are great, but they don’t really scale, do they? While it is easy to have a 16x4 table for a simple grid world, the number of possible states in any modern game or real-world environment is nearly infinitely larger. For most interesting problems, tables simply don’t work. We instead need some way to take a description of our state, and produce Q-values for actions without a table: that is where neural networks come in. By acting as a function approximator, we can take any number of possible states that can be represented as a vector and learn to map them to Q-values.
In the case of the FrozenLake example, we will be using a one-layer network which takes the state encoded in a one-hot vector (1x16), and produces a vector of 4 Q-values, one for each action. Such a simple network acts kind of like a glorified table, with the network weights serving as the old cells. The key difference is that we can easily expand the Tensorflow network with added layers, activation functions, and different input types, whereas all that is impossible with a regular table. The method of updating is a little different as well. Instead of directly updating our table, with a network we will be using backpropagation and a loss function. Our loss function will be sum-of-squares loss, where the difference between the current predicted Q-values, and the “target” value is computed and the gradients passed through the network. In this case, our Q-target for the chosen action is the equivalent to the Q-value computed in equation 1 above.
Eq2. Loss = ∑(Q-target - Q)²
Below is the Tensorflow walkthrough of implementing our simple Q-Network:
