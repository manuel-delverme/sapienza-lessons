package multiagent;

import java.io.*;

/**
 * This class represents a task in the world and is associated to a cell.
 * The task status is defined according to an Enum.
 *
 * @author Albani Dario
 * @version 1.0
 */
public class Task implements Serializable {
	private static final long serialVersionUID = 1L;

	/**
	 * This class represents a task status:
	 * <p> visit: the cell has to be visited
	 * <p> spray: the robot needs to remove the weed in the cell
	 *
	 * @author Albani Dario
	 * @version 1.0
	 */
	public static enum Status {
		VISIT, SPRAY, DONE
	}

	/**
	 * the cell associated to the task
	 */
	protected Cell cell;

	/**
	 * The associated cell.
	 */
	private Status status;

	/**
	 * The agent that accomplished the task
	 */
	private int completedByAgent;

	/**
	 * Constructor for the Task.
	 * A task must have a status when created.
	 */
	public Task(Cell cell, Status status) {
		this.cell = cell;
		this.status = status;
	}

	/**
	 * Return if the task is completed
	 */
	public boolean isDone() {
		return this.status == Status.DONE;
	}

	/**
	 * A task is marked as complete if the associated Cell has been visited or sprayed (according to the exercise)
	 */
	public void markAsComplete(int agent) {
		this.status = Status.DONE;
		this.completedByAgent = agent;
	}

	/**
	 * Return the agent that accomplished the task
	 */
	public int getCompletedByAgent() {
		return this.completedByAgent;
	}

	public Cell getCell() {
		return cell;
	}

	public void setCell(Cell cell) {
		if (cell == null)
			throw new NullPointerException("Trying to assing a null cell to a Task");
		this.cell = cell;
		this.cell.task = this;
	}

	public Status getStatus() {
		return status;
	}

	public void setStatus(Status status) {
		this.status = status;
	}
}
