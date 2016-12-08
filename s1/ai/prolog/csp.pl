:- use_module(library(clpfd)).

logical_constraints(Vars) :-
    Vars = [A, B, C, D],
    Vars ins 1..4,
    A #= B,
    C #= D,
    label(Vars).
