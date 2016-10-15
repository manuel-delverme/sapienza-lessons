nautral_numbers(0).
nautral_numbers(s(X)) :- natural_number(X).

plus(0, X, X) :- natural_number(X).
plus(s(X), Y, s(Z)) :- natural_number(X).
