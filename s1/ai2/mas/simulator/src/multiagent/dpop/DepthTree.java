package multiagent.dpop;

import java.util.Collections;
import java.util.LinkedList;

import multiagent.Agent;
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
	private LinkedList<Node> nodes;
	private World world;

	/**
	 * Constructor
	 *
	 * @param world,      the instance of the world
	 * @param numOfNodes, number of nodes for the current tree
	 */
	public DepthTree(World world, int numOfNodes) {
		this.nodes = new LinkedList<Node>();
		this.world = world;
		for (int n = 0; n < numOfNodes; n++) {
			this.nodes.add(new Node(n, this.world.getUncompletedTask().size()));
		}
	}

	/**
	 * Define a new edge for the tree.
	 *
	 * @param parent.   the parent node
	 * @param child.    the child node
	 * @param isPseudo, define if the edge represent an edge for a pseudo parent
	 */
	public void addNewEdge(int parent, int child, boolean isPseudo) {
		Edge e = new Edge(this.nodes.get(parent), this.nodes.get(child), isPseudo);
		this.nodes.get(parent).addEdge(e);
		this.nodes.get(child).addEdge(e);
	}

	/**
	 * Add the logic to solve you DPOP problem from here
	 */
}