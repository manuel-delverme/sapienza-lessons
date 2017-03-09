package multiagent.dpop;

import java.text.MessageFormat;
import java.util.*;
import java.util.stream.Collectors;

import multiagent.Task;
import multiagent.World;

/**
 * This class offers all the function that you need to manage a DFTree for the DPOP problem.
 * The nodes in the tree are stored into and array with a fixed order, since dealing
 * with a DFTree the numbering of the nodes represents also the position of the
 * nodes in the array.
 * <p>
 * Node numbering starts from 0 and ends at N-1.
 * <p>
 * For instance, you can use this package to generate a tree as in the last slides of the practical lecture:
 * DCOPTree.addNewEdge(0, 1, false);
 * DCOPTree.addNewEdge(1, 2, false);
 * DCOPTree.addNewEdge(1, 3, false);
 *
 * @author Albani Dario
 */
public class DepthTree {
	private final Node root;
	private final World world;
	private LinkedList<Node> nodes;
	private HashSet<Node> pseudo_leaves = new HashSet<>();
	private LinkedList<Task> tasks_snapshot;

	/**
	 * Constructor
	 *
	 * @param world,      the instance of the world
	 */
	public DepthTree(World world) {
		this.nodes = new LinkedList<>();
		this.world = world;
		this.tasks_snapshot = world.getUncompletedTask();
		this.populate_graph(world);

		Comparator<Node> connectedness = (n1, n2) -> n1.getChildren().size() - n2.getChildren().size();
		PriorityQueue<Node> pq = new PriorityQueue<>(world.getNumAgents(), connectedness);
		pq.addAll(this.nodes);

		// find best (pq)
		Node root = pq.remove();
		this.root = root;
		this.build_tree(root, pq);
		this.print_tree(root);
		this.propagateValue();
	}

	private void print_tree(Node root) {
		Set<Node> currentLevel = new HashSet<>();
		Set<Node> nextLevel = new HashSet<>();
		Set<Node> printed = new HashSet<>();
		currentLevel.add(root);

		while (!printed.containsAll(currentLevel)) {
			for (Node father : currentLevel) {
				nextLevel.addAll(father.getChildren());
				if (!printed.contains(father)) {
					System.out.print(MessageFormat.format("{0} -> {1}; ", father, father.getChildren()));
					List<Edge> pseudo = father.getEdges()
							.stream()
							// .filter(Edge::isPseudo)
							.collect(Collectors.toList());

					System.out.println(MessageFormat.format("leaf?: {0}; edges: {1};", pseudo_leaves.contains(father), pseudo));
				}
			}
			currentLevel.removeAll(printed);
			printed.addAll(currentLevel);
			currentLevel = nextLevel;
			nextLevel = new HashSet<>();
			if (!printed.containsAll(currentLevel)) {
				System.out.println("|");
				System.out.println("V");
			}
		}
	}

	private void build_tree(Node root, PriorityQueue<Node> pq) {
		if (pq.isEmpty()) {
			this.pseudo_leaves.add(root);
			return;
		}

		Node best_branch = null;
		for (Node n : pq) {
			if (root.getNeighbours().contains(n)) {
				best_branch = n;
				pq.remove(n);
				break;
			}
		}
		build_tree(best_branch, pq);
		// TODO: it breaks on non fully connected graphs, since it only consider 1 edge
		root.depseudify_edge(best_branch);
	}

	private void populate_graph(World world) {
		this.nodes.addAll(
				world.getAgents()
						.stream()
						.map(robot -> new Node(robot, this.world.getUncompletedTask().size())
						).collect(Collectors.toList()));

		for (Node robot : this.nodes) {
			this.nodes.stream()
					.filter(other_robot -> robot != other_robot)
					.forEach(other_robot -> {
						this.addNewEdge(robot, other_robot, true);
						this.addNewEdge(other_robot, robot, true);
					});
		}
	}

	private void addNewEdge(Node parent, Node child, boolean isPseudo) {
		Edge e = new Edge(parent, child, isPseudo);
		this.nodes.get(parent.getId() - 1).addEdge(e);
		this.nodes.get(child.getId() - 1).addEdge(e);
	}

	public void propagateValue() {
		LinkedList<Task> tasks = this.tasks_snapshot;
		Set<Node> currentLevel = new HashSet<>();
		Set<Node> nextLevel = new HashSet<>();
		currentLevel.addAll(this.pseudo_leaves);

		/*
			take 1 leaf
			calculate util for leaf x parent_i
			propagate to parent_i
		 */
		while (!currentLevel.isEmpty()) {
			// for each layer
			for (Node child : currentLevel) {
				// build task x task matrix
				System.out.println(MessageFormat.format("value table: {0}); ", child));
				child.build_value_table(tasks);
				child.print_value_table();
				child.child_consider_messages();
				System.out.println("considering message");
				child.print_value_table();
				child.calculate_util_message();

				Node parent = child.getParent();
				if (parent != null) {
					nextLevel.add(parent);
				}
			}
			currentLevel = nextLevel;
			nextLevel = new HashSet<>();
		}
		currentLevel.add(this.root);
		while (!currentLevel.isEmpty()) {
			for (Node father : currentLevel) {
				father.choose_best();
				for (Node child : father.getChildren()) {
					System.out.println(MessageFormat.format("propagating util: R({0}); ", child.getId()));
					// build task x task matrix
					child.choose_best();
					// System.out.println(MessageFormat.format(" util message: R({0},{1}); ", child.getParent(), child.getDestination()));
					nextLevel.add(child);
				}
			}
			currentLevel = nextLevel;
			nextLevel = new HashSet<>();
		}
	}

	public Task getNextTask(int agId) {
		Node node = this.nodes.get(agId - 1);
		int task_id = node.getChoice();
		Task task = this.tasks_snapshot.get(task_id);
		System.out.println(MessageFormat.format("assigning {0} to {1}; ", task.getCell(), node));
		return task;
	}

	public void refreshTree(LinkedList<Task> new_tasks) {
		this.tasks_snapshot = new_tasks;
		// this.populate_graph(world);
		// Comparator<Node> connectedness = (n1, n2) -> n1.getChildren().size() - n2.getChildren().size();
		// PriorityQueue<Node> pq = new PriorityQueue<>(world.getNumAgents(), connectedness);
		// pq.addAll(this.nodes);
		for (Node node : this.nodes) {
			node.setNumber_of_tasks(new_tasks.size());
		}

		// find best (pq)
		// Node root = pq.remove();
		// this.root = root;
		// this.build_tree(root, pq);
		// this.print_tree(root);
		this.propagateValue();
	}
}
