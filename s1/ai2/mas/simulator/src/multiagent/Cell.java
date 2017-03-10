package multiagent;

import java.io.*;
import java.text.MessageFormat;

/**
 * This class represents a cell of the World.
 *
 * @author Albani Dario
 * @author Federico Patota
 * @author Gabriele Buondonno
 * @version 1.0 - May 22, 2013
 */
public class Cell implements Serializable {
	private static final long serialVersionUID = 1L;
	/**
	 * Location of the task this Cell is associated to (initially null)
	 */
	protected Task task;
	/**
	 * The status of the Cell.
	 */
	private boolean visited = false;
	private boolean weed = false;
	private boolean sprayed = false;
	/**
	 * Cell coordinates
	 */
	private int row;
	private int col;
	/**
	 * The Agent that has visited this Cell or that has requested to execute
	 * an action relative to this cell (-1 if there is no agent).
	 */
	private int agent = -1;

	/**
	 * Creates a new Cell
	 */
	public Cell(int row, int col) {
		this.row = row;
		this.col = col;
	}

	/**
	 * Creates a new Cell
	 */
	public Cell(int row, int col, Task task) {
		this.task = task;
		this.row = row;
		this.col = col;
	}

	/**
	 * Creates a new Cell
	 */
	public Cell(int row, int col, boolean visited, boolean weed, boolean sprayed, Task task) {
		this.row = row;
		this.col = col;
		this.visited = visited;
		this.weed = weed;
		this.sprayed = sprayed;
		this.task = task;
	}

	/**
	 * Getter and Setter for the cell status
	 */

	public boolean isVisited() {
		return this.visited;
	}

	public void setVisited(boolean visited) {
		this.visited = visited;
	}

	public boolean isWeed() {
		return this.weed;
	}

	public void setWeed(boolean weed) {
		this.weed = weed;
	}

	public boolean isSprayed() {
		return this.sprayed;
	}

	public void setSprayed(boolean sprayed) {
		this.sprayed = sprayed;
	}

	/**
	 * Getter and setter for cell position
	 */
	public int getRow() {
		return this.row;
	}

	public void setRow(int row) {
		this.row = row;
	}

	public int getCol() {
		return this.col;
	}

	public void setCol(int col) {
		this.col = col;
	}

	/**
	 * Getter and setter for the task associated with the cell
	 */
	public Task getTask() {
		return this.task;
	}

	public void setTask(Task task) {
		if (task == null)
			throw new NullPointerException("Trying to assing a null task to a Cell");
		this.task = task;
		this.task.cell = this;
	}

	/**
	 * Returns the Agent associated to this Cell.
	 * The Agent associated to this cell is the one that has visited it or that
	 * has requested to execute an action relative to this cell. If there is no
	 * such agent, -1 is returned.
	 *
	 * @return the Agent associated to this Cell. If there is no such agent, -1.
	 */
	public int getAgent() {
		return this.agent;
	}

	/**
	 * Sets the Agent associated to this Cell.
	 * The Agent associated to this cell is the one that has visited it or that
	 * has requested to execute an action relative to this cell (-1 if there is no agent).
	 */
	public void setAgent(int ag) {
		agent = ag;
	}

	@Override
	public boolean equals(Object o) {
		if (o == null || o.getClass() != this.getClass())
			return false;
		if (o == this)
			return true;
		Cell c = (Cell) o;
		return row == c.row && col == c.col;
	}

	public String toString() {
		return MessageFormat.format("[{0},{1}]", this.getRow(), this.getCol());
	}
}