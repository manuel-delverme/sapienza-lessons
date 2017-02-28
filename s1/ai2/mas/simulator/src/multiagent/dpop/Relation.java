package multiagent.dpop;

import java.util.Collections;
import java.util.LinkedList;

/**
 * Class used to simulate a relation table as for the DPOP problem.
 * Use this to store and propagate utility values bottom up in the tree.
 *
 * @author Albani Dario
 */
class Relation {
	private Node child;
	private Node parent;

	private LinkedList<LinkedList<Integer>> utilValues;
	private LinkedList<Integer> utilMessage;

	public boolean updated = false;

	public Relation(Node child, Node parent, int numOfVariables) {
		this.child = child;
		this.parent = parent;
		this.utilMessage = new LinkedList<>();
		this.utilValues = new LinkedList<>();
		for (int i = 0; i < numOfVariables; i++) {
			LinkedList<Integer> zeros = new LinkedList<Integer>();
			for (int j = 0; j < numOfVariables; j++) {
				zeros.add(0);
			}
			this.utilValues.add(zeros);
		}
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

	protected LinkedList<LinkedList<Integer>> getUtilValues() {
		return utilValues;
	}

	protected void setUtilValues(LinkedList<LinkedList<Integer>> utilValues) {
		this.utilValues = utilValues;
		this.updateUtilMessage();
	}

	/**
	 * Update the value at position row, col with the new given value
	 *
	 * @param row,      the variable related to the children node
	 * @param col,      the variable related to the parent node
	 * @param newValue, the new value to update
	 */
	protected void updateValue(int row, int col, int newValue) {
		this.utilValues.get(row).add(col, newValue);
		this.utilValues.get(row).remove(col + 1);
		this.updateUtilMessage();
	}

	/**
	 * Update the utility message with the new values in input.
	 * This method is call every time an update occur in the utility table of
	 * the relation.
	 */
	private void updateUtilMessage() {
		this.utilMessage.clear();

		for (LinkedList<Integer> column : this.utilValues) {
			this.utilMessage.add(Collections.max(column));
		}
	}

	public LinkedList<Integer> getUtilMessage() {
		return this.utilMessage;
	}

	/**
	 * Implements the join between two different utility messages.
	 * this and util must be of the same length.
	 *
	 * @return a single utility message that is the element wise sum of the two in input
	 */
	public LinkedList<Integer> joinUtilMessages(LinkedList<Integer> util) {
		//TODO
		return null;
	}

	/**
	 * Implements the projection of an utility message into the utility table
	 * of this relation as defined in the DPOP framework.
	 *
	 * @param util, must have the same number of column as the current util table
	 * @return a single utility message
	 */
	public LinkedList<Integer> projectUtilMessages(LinkedList<Integer> util) {
		//TODO
		return null;
	}

	@Override
	public boolean equals(Object o) {
		Relation r = (Relation) o;
		return (this.child.equals(r.getChild()) && this.parent.equals(r.getParent())) ||
				(this.parent.equals(r.getChild()) && this.child.equals(r.getParent()));
	}

}
