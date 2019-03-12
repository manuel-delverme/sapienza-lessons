def add_model(dikt, name, klass, const, space):
  if isinstance(space, tuple):
    space = list(space)
  assert isinstance(space, list)
  assert isinstance(space[0], dict)
  dikt[name] = [klass, const, space]

  # space =[ {'name': 'var_1', 'type': 'continuous', 'domain':(-1,1), 'dimensionality':1},
  #          {'name': 'var_2', 'type': 'continuous', 'domain':(-3,1), 'dimensionality':2},
  #          {'name': 'var_3', 'type': 'bandit', 'domain': [(-1,1),(1,0),(0,1)], 'dimensionality':2},
  #          {'name': 'var_4', 'type': 'bandit', 'domain': [(-1,4),(0,0),(1,2)]},
  #          {'name': 'var_5', 'type': 'discrete', 'domain': (0,1,2,3)}]
