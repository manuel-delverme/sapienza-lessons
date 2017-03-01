package multiagent;

import java.util.*;
import java.io.*;

/**
 * This class implements a UAV.
 * <p>
 * ===================      README      ======================
 * <p>
 * NOT ALL THE ACTION IN THE CURRENT CLASS HAVE TO BE DEFINED.
 * Think carefully to what you choose to do and complete
 * the action needed by your implementation.
 * IF YOU THINK that your implementation needs more methods
 * than those here proposed, you can implement them.
 * Be careful to follow the guidelines and be ready to
 * motivate your changes.
 * ===========================================================
 *
 * @author Albani Dario
 * @author Federico Patota
 * @author Gabriele Buondonno
 * @version 1.0 - May 22, 2013
 */
public class Agent implements Serializable {
	private static final long serialVersionUID = 1L;

	/**
	 * Identifier for this agent.
	 */
	private final int id;

	/**
	 * current position of the agent.
	 */
	private Cell position;

	/**
	 * task currently under execution by this agent.
	 */
	private Task currentTask;

	/**
	 * action currently under execution by this agent.
	 */
	private Action currentAction;

	/**
	 * Tasks assigned to any agent yet.
	 */
	private LinkedList<Task> pendingTasks = new LinkedList<Task>();

	/**
	 * instance of the current world class on which the agent is acting
	 **/
	private World world;

	/**
	 * Constructor for this class.
	 *
	 * @param id    identifier for this agent.
	 * @param c     initial agent position.
	 * @param world an instance of the world used to retrieve information and tasks
	 */
	public Agent(int id, Cell c, World world) {
		this.id = id;
		this.world = world;
		position = c;
		currentAction = Action.publishNextTask;
	}

	/**
	 * Returns the agent identifier.
	 *
	 * @return this agent identifier.
	 */
	public int getId() {
		return id;
	}

	/**
	 * Returns the current position of the agent.
	 *
	 * @return the current position of this agent.
	 */
	public Cell getPosition() {
		return position;
	}

	/**
	 * Returns the task currently under execution by the agent.
	 *
	 * @return the task currently under execution by this agent.
	 */
	public Task getCurrentTask() {
		return currentTask;
	}

	/**
	 * Checks whether the pending tasks list is empty.
	 *
	 * @return true if the pending tasks list is empty, otherwise false.
	 */
	public boolean emptypTask() {
		return pendingTasks.isEmpty();
	}

	/**
	 * Adds this cell to the pending tasks list only if has weeds and is not harvested
	 */
	public void addpTask(Task t) {
		if (t.getCell().isWeed() && !t.getCell().isSprayed())
			pendingTasks.add(t);
	}

	/**
	 * Removes this location from the pending tasks list.
	 */
	public void removepTask(Task t) {
		pendingTasks.remove(t);
	}

	/**
	 * Returns a pending task from the pending tasks list, according to some priority.
	 * If the list is empty, it returns null.
	 *
	 * @return the next pending task to be auctioned.
	 */
	public Task getNextpTask() {
		if (pendingTasks.isEmpty()) return null;
		return pendingTasks.get(0);
	}

	/**
	 * The world calls this method to ask the agent for the next action to be executed.
	 * The agent returns the action currently under execution.
	 *
	 * @return the action that needs to be executed.
	 */
	public Action nextAction() {
		if(!this.getPosition().isVisited() && this.getCurrentTask().getCell() == this.getPosition())
		{
			return Action.check;
		}
		return currentAction;
	}

	/**
	 * Deletes current task setting it to null.
	 */
	public void cancelTask() {
		this.currentTask = null;
	}

	/**
	 * The simulator asks the agent to allocate the pending tasks.
	 * The pending tasks are either the list of pending tasks available in the current class
	 * or the task still available in the world (this depend to your implementation).
	 * The tasks are immediately assigned according to the specification of your exercise.
	 * The agent list is provided by the simulator.
	 *
	 * @param agents the agents list.
	 */
	public void assignTasks(List<Agent> agents) {

		Task task;
		for(Agent agent: agents){
			if(pendingTasks.isEmpty())
				break;
			task = pendingTasks.pop();
			agent.addpTask(task);
		}
		System.out.print("XXX: TODO: you should find a way to assign a new task\n");
		// TODO Complete
	}

	/**
	 * CNP - implement your own logic (e.g. for CNP the agent is the manager of task)
	 * <p>
	 * The simulator asks the agent to allocate the pending tasks.
	 * The pending tasks are either the list of pending tasks available in the current class
	 * or the task still available in the world (this depend to your implementation).
	 * The tasks are immediately assigned according to the specification of your exercise.
	 * The agent list is provided by the simulator.
	 *
	 * @param agents the agents list.
	 */
	public void assignTasks(List<Agent> agents, Task task) {
		System.out.print("TODO: you should find a way to assign a new task\n");
		for (Agent a : agents) {
			a.bidForTask(task);
			//continue
		}
	}

	/**
	 * This method is called by the simulation environment to inform
	 * the agent about the outcome of its action, as provided by the World.
	 *
	 * @param nextPosition the agent new position.
	 * @param nextTask     a new task discovered by this agent. If null, there is no next task.
	 */
	public void updateState(Cell nextPosition, Task nextTask) {
		//Some tips:
		// If the agent is in the same cell as nextPosition maybe it needs to 
		// either move or check/spray
		// Do not forget the noOp operation that is used to terminate the simulation (is one of the condition in or)
		if (nextTask.getCell() != nextPosition) {
			System.out.println("[AGENT] didn't arrive yet, currAct = move; teleporting");
			this.currentAction = Action.moveToLocation;
		} else {
			System.out.println("[AGENT] im in the goal cell");
			if(nextTask.getCell().isVisited()){
				System.out.println("[AGENT] was visited, currAct = publish");
				this.currentAction = Action.publishNextTask;
			} else {
				System.out.println("[AGENT] wasnt visited, currAct = check");
				this.currentAction = Action.check;
			}
		}
		this.currentTask = nextTask;
	}


	/**
	 * The requests for Bids are issued by the agent.
	 * In the first implementation an agent can only bid if it has no current task.
	 *
	 * @param task the task which the request is issued for.
	 * @return a bid for the given task.
	 */
	public Bid bidForTask(Task task) {
		System.out.print("TODO: are you dealing with auctions and CNP?\n");
		// TODO Complete
		return null;
	}

	/**
	 * The acceptance requests are issued by the agent.
	 * In the first implementation an agent can only accept if it has no current task.
	 *
	 * @param task the task which the request is issued for.
	 * @return true if the task is accepted.
	 */
	public boolean acceptTask(Task task) {
		System.out.print("TODO: how am I supposed to accept the task?\n");
		// TODO Complete
		return false;
	}
}
