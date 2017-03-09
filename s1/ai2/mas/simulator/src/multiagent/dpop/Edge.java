package multiagent.dpop;

import java.text.MessageFormat;

/**
 * Silly representation of an edge used for the DCOP problem.
 * Can be used to represent an edge in a constraint graph or in a tree.
 * For the tree structure you can assume source as the parent of the destination destination.
 * Edges are bidirectional, i.e. edge(o1,o2) == edge(o2,01).
 *
 * @author Albani Dario
 **/
class Edge {
	private Node source;
	private Node destination;

	private boolean isPseudo = false;

	public Edge(Node id, Node id2) {
		this.setSource(id);
		this.setDestination(id2);
	}

	public Edge(Node id, Node id2, boolean isPseudo) {
		this.setSource(id);
		this.setDestination(id2);
		this.setPseudo(isPseudo);
	}

	protected Node getSource() {
		return source;
	}

	protected void setSource(Node source) {
		this.source = source;
	}

	protected Node getDestination() {
		return destination;
	}

	protected void setDestination(Node destination) {
		this.destination = destination;
	}

	protected boolean isPseudo() {
		return isPseudo;
	}

	void setPseudo(boolean isPseudo) {
		this.isPseudo = isPseudo;
		if (isPseudo) {
			this.source.remove_relation(destination);
			this.destination.remove_relation(source);
		} else {
			this.source.add_relation(destination);
			this.destination.add_relation(source);
		}
	}

	@Override
	public boolean equals(Object o) {
		Edge e = (Edge) o;
		return (this.source == e.getSource() && this.destination == e.getDestination());
		// || (this.source == e.getDestination() && this.destination == e.getSource());
	}

	public String toString() {
		String arrow = "=====>";
		if (this.isPseudo()) {
			arrow = " - >";
		}
		return MessageFormat.format("{0}{2}{1}", this.getSource(), this.getDestination(), arrow);
	}
}
