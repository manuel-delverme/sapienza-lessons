package multiagent.dpop;

import multiagent.Agent;
import multiagent.Task;

import java.awt.*;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * This class represent a node in the tree.
 * Such node is structured to let you use it for the DPOP solution.
 *
 * @author Albani Dario
 */

class Node {
	private final Agent robot;
	private final int max_val;
	int[][] utilValues;
	private int id;
	// the number of variables to be managed by the node during the DPOP execution
	// e.g following the example on the practical slide this could be [a,b,c], then 3.
	private int number_of_tasks;
	private LinkedList<Edge> edges;
	private LinkedList<Relation> relations;
	private int choice;
	private Component neighbours;

	/**
	 * Constructor for the node (an agent)
	 *
	 * @param robot,             the agent object in World
	 * @param number_of_tasks, the number of variables to be managed by the agent (i.e. Tasks)
	 */
	public Node(Agent robot, int number_of_tasks) {
		this.id = robot.getId();
		this.number_of_tasks = number_of_tasks;
		this.relations = new LinkedList<>();
		this.robot = robot;
		this.edges = new LinkedList<>();
		utilValues = new int[this.number_of_tasks][this.number_of_tasks];
		this.max_val = Integer.MIN_VALUE;
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

	LinkedList<Edge> getEdges() {
		return edges;
	}

	protected void setEdges(LinkedList<Edge> edges) {
		this.edges = edges;
	}

	void depseudify_edge(Node childToKeep) {
		Edge e;
		for (int other_node_idx = 0; other_node_idx < this.edges.size(); other_node_idx++) {
			e = this.edges.get(other_node_idx);
			if (e.getDestination() != childToKeep) {
				continue;
			}
			e.setPseudo(false);
			this.edges.set(other_node_idx, e);
		}
	}

	void addEdge(Edge e) {
		if (this.edges.contains(e)) {
			return;
		}
		this.edges.add(e);
		if (!e.isPseudo())
			this.relations.add(new Relation(e.getSource(), e.getDestination(), number_of_tasks));
	}

	/**
	 * @return true if this is the root
	 */
	protected boolean isRoot() {
		return this.getParent() == null;
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
	private LinkedList<Node> getParents() {
		return this.edges
				.stream()
				.filter(e -> e.getDestination() == this)
				.map(Edge::getSource)
				.collect(Collectors.toCollection(LinkedList::new));
	}

	Node getParent() {
		for (Edge e : this.edges) {
			if (e.getDestination() == this && !e.isPseudo()) {
				return e.getSource();
			}
		}
		return null;
	}

	/**
	 * Retrieve all the children node of this
	 * <p>
	 * NOTE if the list is empty, this is a leaf
	 *
	 * @return a list of children
	 */
	LinkedList<Node> getChildren() {
		return this.edges
				.stream()
				.filter(e -> e.getSource() == this && !e.isPseudo())
				.map(Edge::getDestination)
				.collect(Collectors.toCollection(LinkedList::new));
	}

	/**
	 * @return the number_of_tasks
	 */
	protected int getNumber_of_tasks() {
		return number_of_tasks;
	}

	/**
	 * @param number_of_tasks the number_of_tasks to set
	 */
	protected void setNumber_of_tasks(int number_of_tasks) {
		this.number_of_tasks = number_of_tasks;
	}

	@Override
	public boolean equals(Object o) {
		Node e = (Node) o;
		return this.id == e.getId();
	}

	public String toString() {
		return Integer.toString(this.getId());
	}

	Agent getRobot() {
		return robot;
	}

	void remove_relation(Node node2) {
		for (Relation r : this.relations) {
			if (
					r.getParent() == this && r.getChild() == node2
							||
							r.getParent() == node2 && r.getChild() == this) {
				this.relations.remove(r);
				break;
			}
		}
	}

	void choose_best() {
		int best_task_id = 0;
		int their_task;
		if (this.isRoot()) {
			their_task = 0;
		} else {
			their_task = this.getParent().getChoice();
		}
		int best_task_value = this.utilValues[0][their_task];
		for (int my_task_id = 1; my_task_id < this.number_of_tasks; my_task_id++) {
			int task_value = this.utilValues[my_task_id][their_task];
			if (task_value > best_task_value) {
				best_task_value = task_value;
				best_task_id = my_task_id;
			}
		}
		this.choice = best_task_id;
	}

	void build_value_table(List<Task> tasks) {
		for (int my_task = 0; my_task < this.number_of_tasks; my_task++) {
			int displacement = this.getRobot().calculate_distance_to_cell(tasks.get(my_task).getCell());
			if (!this.isRoot()) {
				for (int their_task = 0; their_task < this.number_of_tasks; their_task++) {
					//TODO turn n^2 to n by precalculating emptiness and displacement
					int emptiness = -this.getParent().getRobot().calculate_distance_to_cell(tasks.get(their_task).getCell());
					int value = -(displacement - emptiness);
					this.utilValues[my_task][their_task] = value;
				}
			} else {
				this.utilValues[my_task][0] = -displacement;
			}
		}
	}

	void child_consider_messages() {
		for (Relation r : this.getRelations()) {
			if (r.getChild() == this) continue;

			for (int my_task = 0; my_task < this.number_of_tasks; my_task++) {
				int deeper_information = r.utilMessage[my_task];
				for (int their_task = 0; their_task < this.number_of_tasks; their_task++) {
					this.utilValues[my_task][their_task] += deeper_information;
				}
			}
		}
	}

	void calculate_util_message() {
		int downstream_val;
		// for each upstream action
		int[] utilMessage = new int[this.number_of_tasks];

		for (int their_task = 0; their_task < this.number_of_tasks; their_task++) {
			int max = this.utilValues[0][their_task];
			// find the best one
			// BEWARE CACHE MISSES!
			for (int my_task = 1; my_task < this.number_of_tasks; my_task++) {
				downstream_val = this.utilValues[my_task][their_task];
				if (downstream_val > max) {
					max = downstream_val;
				}
			}
			utilMessage[their_task] = max;
		}
		if (!this.isRoot()) {
			Node parent = this.getParent();
			Relation relation = this.getRelation(parent);
			relation.setUtilMessage(utilMessage);
		}
	}


	int getChoice() {
		return choice;
	}

	void print_value_table() {
		for (int my_task = 0; my_task < 10; my_task++) {
			for (int their_task = 0; their_task < 10; their_task++) {
				System.out.print(this.utilValues[my_task][their_task] + "\t");
			}
			System.out.print("\n");
		}
	}

	HashSet<Node> getNeighbours() {
		return this.edges
				.stream()
				.filter(e -> e.getSource() == this)
				.map(Edge::getDestination)
				.collect(Collectors.toCollection(HashSet::new));
	}

	void add_relation(Node destination) {
		this.relations.add(new Relation(this, destination, this.number_of_tasks));
	}
}
