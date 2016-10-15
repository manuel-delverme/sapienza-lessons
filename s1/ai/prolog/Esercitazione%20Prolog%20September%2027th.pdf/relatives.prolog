father(daniele, michela).
mother(alma, eriberto).
father(daniele, jacopo).
mother(annamaria, daniele).
father(eriberto, daniele).
mother(annamaria, marcello).
father(antonio, eriberto).
mother(annamaria, sandro).

grandfather(X, Z) :- father(X, Y), father(Y, Z).
grandfather(X, Z) :- father(X, Y), mother(Y, Z).
nice(michela).
nice(anna).