%
Wls = inv(X'*X)*X'*d
% since X'X ^ -1 can be singular, add a dI as regularization parameter
Wls = inv(X'*X - d*I)*X'*d