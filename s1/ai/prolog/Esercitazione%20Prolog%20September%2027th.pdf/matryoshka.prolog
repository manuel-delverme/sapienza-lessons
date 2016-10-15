in(olga, katarina).
in(natasha, olga).
in(irina, natasha).

in(X, X).
in(X, Y) :- in(X, Doll), in(Doll, Y).
