arc(a, b).
arc(a, c).
arc(b, d).
arc(c, d).
arc(d, e).
arc(f, g).

connected(Node, Node).
connected(Node1, Node2) :- arc(Node1, MiddleNode), connected(MiddleNode, Node2).