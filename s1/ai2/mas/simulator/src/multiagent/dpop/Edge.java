package multiagent.dpop;

/**
 * Silly representation of an edge used for the DCOP problem.
 * Can be used to represent an edge in a constraint graph or in a tree.
 * For the tree structure you can assume node1 as the parent of the child node2.
 * Edges are bidirectional, i.e. edge(o1,o2) == edge(o2,01).
 *
 * @author Albani Dario
 **/
class Edge {
	private Node node1;
	private Node node2;

	private boolean isPseudo = false;

	public Edge(Node id, Node id2) {
		this.setNode1(id);
		this.setNode2(id2);
	}

	public Edge(Node id, Node id2, boolean isPseudo) {
		this.setNode1(id);
		this.setNode2(id2);
		this.setPseudo(isPseudo);
	}

	protected Node getNode1() {
		return node1;
	}

	protected void setNode1(Node node1) {
		this.node1 = node1;
	}

	protected Node getNode2() {
		return node2;
	}

	protected void setNode2(Node node2) {
		this.node2 = node2;
	}

	protected boolean isPseudo() {
		return isPseudo;
	}

	protected void setPseudo(boolean isPseudo) {
		this.isPseudo = isPseudo;
	}

	@Override
	public boolean equals(Object o) {
		Edge e = (Edge) o;
		return (this.node1 == e.getNode1() && this.node2 == e.getNode2())
				|| (this.node1 == e.getNode2() && this.node2 == e.getNode1());
	}
}
