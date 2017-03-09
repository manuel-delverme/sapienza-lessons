package multiagent;

import multiagent.dpop.DepthTree;

import java.io.*;
import java.util.*;

/**
 * This class implements a full simulator.
 *
 * @author Albani Dario
 * @author Federico Patota
 * @author Gabriele Buondonno
 * @version 1.0 - May 22, 2013
 */

public class AgentSim implements Serializable {
	private static final long serialVersionUID = 1L;

	/**
	 * The agents
	 */
	public List<Agent> agents;
	/**
	 * The world
	 */
	public World world;
	/**
	 * The agent currently executing an action (used for simulation purposes)
	 */
	private int currentAgent;

	/**
	 * Counter used to check if the exploration process has ended.
	 */
	private int inactiveSteps = 0;

	/**
	 * Number of a Actions performed (used for statistics).
	 */
	private int totalNoOps;
	private int totalMoveToLocation;
	private int totalNextTask;

	/**
	 * Constructs a simulator creating a new world with the specified characteristics.
	 *
	 * @param height the height of the world
	 * @param width  the width of the world
	 */
	public AgentSim(int height, int width) {
		world = new World(height, width);
	}

	/**
	 * Constructs a simulator creating a new world with the specified characteristics.
	 *
	 * @param height the height of the world
	 * @param width  the width of the world
	 * @param weed   the number of inaccessible cells
	 * @param ags    the number of agents
	 */
	public AgentSim(int height, int width, int weed, int ags) {
		world = new World(height, width);
		addWeedCells(weed);
		initTasks();
		initAgentsRandom(ags);
		world.setTaskAssigner(new DepthTree(world));
	}

	/**
	 * Adds weeds in cells.
	 *
	 * @param weed the number of weed cells that we want to add
	 */
	public void addWeedCells(int weed) {
		world.addWeedCells(weed);
	}

	/**
	 * Positions agents in the world in random positions.
	 */
	public void initAgentsRandom(int numAgents) {
		agents = new LinkedList<Agent>();
		for (int i = 1; i <= numAgents; i++) {
			Cell cell = world.getCell((int) (world.getHeight() * Math.random()), (int) (world.getWidth() * Math.random()));
			Agent a = new Agent(i, cell, this.world);
			agents.add(a);

			cell.setVisited(true);
			if (cell.isWeed()) {
				cell.setSprayed(true);
			}

			if (cell.getTask() != null)
				cell.getTask().markAsComplete(cell.getAgent());
		}
		world.addAgents(agents);
	}

	/**
	 * Task initialization.
	 * <p>
	 * TODO update the task list according to your problem.
	 * Check the setUpForCoverage and setUpForWeed methods in class World
	 */
	public int initTasks() {
		this.world.setUpForCoverage();
//		this.world.setUpForWeed();
		System.out.print("setting up for coverage\n");
		return 0;
	}

	/**
	 * Executes one step for one agent and switches agent.
	 * The one step execution change with respect to the exercise.
	 *
	 * @return true if there have been two full rounds without any action taken,
	 * indicating that the system will have no further evolution.
	 */
	public boolean doOneStep() throws InterruptedException {
		//retrieve the action from the current agent
		Agent agent = agents.get(currentAgent);
		Action act = agent.nextAction();

		if (agent.getId() == 1) {
			Thread.sleep(500);
		}


		//managing statistics and inactive steps count
		if (act == Action.noOp) {
			inactiveSteps++;
			totalNoOps++;
		} else {
			inactiveSteps = 0;
			if (act == Action.moveToLocation)
				this.totalMoveToLocation++;
			else
				this.totalNextTask++;
		}

		//executing the action for the agent and return the new task that has to be executed
		//e.g. move to a task already executed and return the new task computed according to the wanted action
		Task nextTask = world.executeAction(agent.getId(), agent.getCurrentTask(), act);

		//updates the state of the agents with the new agent position and the next task to be performed
		agent.updateState(world.getAgentPosition(agent.getId()), nextTask);

		//assing and validate the next task
//        agent.assignTasks(agents);

		currentAgent = (currentAgent + 1) % agents.size();

		return inactiveSteps >= 2 * agents.size() || this.world.getUncompletedTask().isEmpty();
	}

	//************************************************ Methods to retrieve information about the world and about the simulation ******

	/**
	 * Returns the number of cells with the given status.
	 * Visited.
	 *
	 * @return the number of cells with the given status.
	 */
	public int countVisitedCells() {
		int count = 0;
		for (int row = this.world.getHeight() - 1; row >= 0; row--)
			for (int col = this.world.getWidth() - 1; col >= 0; col--)
				if (this.world.getCell(row, col).isVisited())
					count++;
		return count;
	}

	/**
	 * Returns the number of cells with the given status.
	 * Weed.
	 *
	 * @return the number of cells with the given status.
	 */
	public int countWeedCells() {
		int count = 0;
		for (int row = world.getHeight() - 1; row >= 0; row--)
			for (int col = world.getWidth() - 1; col >= 0; col--)
				if (world.getCell(row, col).isWeed())
					count++;
		return count;
	}

	/**
	 * Returns the number of cells with the given status.
	 * Sprayed.
	 *
	 * @return the number of cells with the given status.
	 */
	public int countUnsprayedCells() {
		int count = 0;
		for (int row = world.getHeight() - 1; row >= 0; row--)
			for (int col = world.getWidth() - 1; col >= 0; col--)
				if (world.getCell(row, col).isSprayed())
					count++;
		return count;
	}

	/**
	 * Returns the total number of cells.
	 *
	 * @return the total number of cells.
	 */
	public int getTotalCells() {
		return world.getWidth() * world.getHeight();
	}

	/**
	 * Returns the number of times the given Action has been called. If the simulation
	 * is over and act==Action.noOp, noOp is subtracted the last series of noOps.
	 *
	 * @param act the action to examine.
	 * @return the number of times the given Action has been called.
	 */
	public int getCalls(Action act) {
		if (act == Action.noOp) {
			return (inactiveSteps < 2 * agents.size() ? totalNoOps : totalNoOps - inactiveSteps);
		}
		if (act == Action.moveToLocation) {
			return this.totalMoveToLocation;
		}
		if (act == Action.publishNextTask) {
			return this.totalNextTask;
		}
		return -1;
	}

	/**
	 * Returns the total number of steps performed. The number of total steps is
	 * equal to getCalls(Action.noOp) + getCalls(Action.nextMoveToTarget) + getCalls(Action.totalNextStepInTask).
	 *
	 * @return the number of total steps performed.
	 */
	public int getTotalSteps() {
		return getCalls(Action.noOp) + this.totalMoveToLocation + this.totalNextTask;
	}

	/**
	 * Returns the total number of complete rounds the simulation has performed.
	 * By performing a round, we mean doing one step for each agent.
	 * The result is rounded by defect.
	 *
	 * @return the number of total loops performed.
	 */
	public int getTotalRounds() {
		return getTotalSteps() / agents.size();
	}

	/**
	 * Returns the number of cells visited by the given agent.
	 *
	 * @param agId the id of the agent
	 */
	public int getVisited(int agId) {
		int count = 0;
		for (int row = world.getHeight() - 1; row >= 0; row--)
			for (int col = world.getWidth() - 1; col >= 0; col--)
				if (world.getCell(row, col).isVisited() && world.getCell(row, col).getAgent() == agId)
					count++;
		return count;
	}

	/**
	 * Convenience method returning a String representation for all the statisics.
	 *
	 * @return a String representation for the statisics.
	 */
	public String statsToString() {
		StringBuilder builder = new StringBuilder();

		builder.append("Total cells: ").append(getTotalCells());
		builder.append("\n---> FILL ME in AgentSim.statsToString()<---\n");
		for (int i = 0; i < this.world.getHeight(); i++) {
			for (int j = 0; j < this.world.getWidth(); j++) {
				if (this.world.getCell(i, j).getTask() != null) {
					builder.append(i).append(" ").append(j).append(" ");
					builder.append(this.world.getCell(i, j).getTask().getStatus());
					builder.append("\n");
				}
			}
		}
		//TODO fill with your information
		//this is the string contained in the pop up that appears at the end of the execution

		return builder.toString();
	}
}
