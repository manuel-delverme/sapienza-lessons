package multiagent.dpop;

import multiagent.Task;

import java.util.LinkedList;
import java.util.List;

/**
 * Class used to simulate a relation table as for the DPOP problem.
 * Use this to store and propagate utility values bottom up in the tree.
 *
 * @author Albani Dario
 */
class Relation {
	private final int number_of_tasks;
	public boolean updated = false;
	// private LinkedList<LinkedList<Integer>> utilValues;
	int[] utilMessage;
	private Node child;
	private Node parent;

	public Relation(Node child, Node parent, int numOfVariables) {
		this.child = child;
		this.parent = parent;
		this.number_of_tasks = numOfVariables;
		utilMessage = new int[this.number_of_tasks];
	}

	protected Node getChild() {
		return child;
	}

	protected void setChild(Node child) {
		this.child = child;
	}

	protected Node getParent() {
		return parent;
	}

	protected void setParent(Node parent) {
		this.parent = parent;
	}

	public int[] getUtilMessage() {
		return this.utilMessage;
	}

	public void setUtilMessage(int[] utilMessage) {
		this.utilMessage = utilMessage;
	}

	/**
	 * Implements the join between two different utility messages.
	 * this and util must be of the same length.
	 *
	 * @return a single utility message that is the element wise sum of the two in input
	 */
	public LinkedList<Integer> joinUtilMessages(LinkedList<Integer> util) {
		/*
		for (int i = 0; i < utilValues.size(); i++) {
			int delta = util.get(i);
			for (int j = 0; j < utilValues.size(); j++) {
				int val = this.utilValues.get(i).get(j);
			}
		}
		for(LinkedList<Integer> row: utilValues){
			utilMessage.add(Collections.max(row));
		}
		return utilMessage;
		*/
		return util; // TODO: RM;FILLER
	}

	@Override
	public boolean equals(Object o) {
		Relation r = (Relation) o;
		return (this.child.equals(r.getChild()) && this.parent.equals(r.getParent())) ||
				(this.parent.equals(r.getChild()) && this.child.equals(r.getParent()));
	}

	void merge_message() {
		// TODO
	}

	public void propagate_choice(Task choice) {

	}
}
