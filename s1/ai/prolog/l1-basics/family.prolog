grandFather(Z, X) :- father(Y, X), father(Z, Y).
grandFather(Z, X) :- father(Y, X), mother(Z, Y).

son(X, Y) :- father(Y, X).
son(X, Y) :- mother(Y, X).

mother(a).
mother(b).
mother(c).
mother(d).