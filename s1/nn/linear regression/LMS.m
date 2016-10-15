X = [1, 2, 3, 4, 5]
D = [100, 120, 120, 130, 180]'
mu = 0.1
W = rand(length(X), length(X))
Y= W*X'
e = Y-D
W = W + mu * e