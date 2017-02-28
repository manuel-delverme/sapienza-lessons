package multiagent.dpop;

import java.util.LinkedList;

/**
 * This class represent a node in the tree.
 * Such node is structured to let you use it for the DPOP solution.
 *
 * @author Albani Dario
 */

class Node {
	private int id;
	// the number of variables to be managed by the node during the DPOP execution
	// e.g following the example on the practical slide this could be [a,b,c], then 3.
	private int numOfVariables;
	private LinkedList<Edge> edges;
	private LinkedList<Relation> relations;

	/**
	 * Constructor for the node (an agent)
	 *
	 * @param id,             a unique id assigned to the node. Must be the same as the agentID
	 * @param numOfVariables, the number of variables to be managed by the agent (i.e. Tasks)
	 */
	public Node(int id, int numOfVariables) {
		this.id = id;
		this.setNumOfVariables(numOfVariables);
		this.relations = new LinkedList<Relation>();
		this.edges = new LinkedList<Edge>();

	}

	/**
	 * Get current node id
	 *
	 * @return int id
	 */
	protected int getId() {
		return id;
	}

	/**
	 * Get current node relations tables as in the DPOP structure
	 *
	 * @return list of relations
	 */
	protected LinkedList<Relation> getRelations() {
		return relations;
	}

	/**
	 * Get the relation table associated with the node in input
	 *
	 * @return relation from this to node or vice versa
	 */
	protected Relation getRelation(Node n) {
		for (Relation r : this.relations) {
			if (r.getChild() == n || r.getParent() == n) {
				return r;
			}
		}
		return null;
	}

	/**
	 * Add or update a relation to the list of relations of the current node.
	 * Use this method to update the relations between the nodes or to add a new one
	 *
	 * @param relation
	 */
	protected void addRelation(Relation relation) {
		for (Relation r : this.relations) {
			if (r.equals(relation)) {
				this.relations.remove(r);
				break;
			}
		}
		this.relations.add(relation);
	}

	protected LinkedList<Edge> getEdges() {
		return edges;
	}

	protected void setEdges(LinkedList<Edge> edges) {
		this.edges = edges;
	}

	protected void addEdge(Edge e) {
		if (this.edges.contains(e)) {
			return;
		}

		this.edges.add(e);
		this.relations.add(new Relation(e.getNode1(), e.getNode2(), numOfVariables));
	}

	/**
	 * @return true if this is the root
	 */
	protected boolean isRoot() {
		return this.getParents().isEmpty();
	}

	/**
	 * @return true if this is a leaf
	 */
	protected boolean isLeaf() {
		return this.getChildren().isEmpty();
	}

	/**
	 * Retrieve all the parents node of this
	 * <p>
	 * NOTE if the list is empty, this is a leaf
	 *
	 * @return a list of parents
	 */
	protected LinkedList<Node> getParents() {
		LinkedList<Node> parents = new LinkedList<Node>();
		for (Edge e : this.edges) {
			if (e.getNode2() == this) {
				parents.add(e.getNode1());
			}
		}

		return parents;
	}

	/**
	 * Retrieve all the children node of this
	 * <p>
	 * NOTE if the list is empty, this is the root
	 *
	 * @return a list of children
	 */
	protected LinkedList<Node> getChildren() {
		LinkedList<Node> children = new LinkedList<Node>();
		for (Edge e : this.edges) {
			if (e.getNode1() == this) {
				children.add(e.getNode2());
			}
		}

		return children;
	}

	/**
	 * @return the numOfVariables
	 */
	protected int getNumOfVariables() {
		return numOfVariables;
	}

	/**
	 * @param numOfVariables the numOfVariables to set
	 */
	protected void setNumOfVariables(int numOfVariables) {
		this.numOfVariables = numOfVariables;
	}

	@Override
	public boolean equals(Object o) {
		Node e = (Node) o;
		return this.id == e.getId();
	}

}
