Python MDP solver (Luca Iocchi, 2015)
-------------------------------------

* mdp.py contains basic domain independent functions for planning and learning with MDP.

* mdp_<problem>.py contains the definition of a particular MDP problem.

How to use

$ python mdp_<problem>.py <Planning|Learning> <n. iterations> <epsilon>

Example:

$ python mdp_grid.py Planning 10

