package multiagent;

import java.util.*;

/**
 * This class represents the world as a grid of Cells and stores the agents Locations.
 * @version 1.1
 * @author Albani Dario
 *
 * @version 1.0 - May 22, 2013
 * @author Federico Patota
 * @author Gabriele Buondonno
 */
public class World{
	/**number of rows of the grid*/
	private int height;
	/**number of columns of the grid*/
	private int width;

	/**stores the state of the world*/
	private Cell[][] map;

	/**stores the cell of the agents*/
	private List<Cell>agentsCells = new ArrayList<Cell>();

	/**stores the agents*/
	private List<Agent>agents = new ArrayList<Agent>();

	/**
	 * Simple constructor creating a world of size nxm
	 */
	public World(int m, int n) {
		height=m;
		width=n;
		map = new Cell[m][n];
		for (int r=0;r<m;r++)
			for (int c=0;c<n;c++)
				map[r][c] = new Cell(r,c);
	}

	/**Returns the number of rows of the world.
	 * @return the number of rows of the world.
	 */
	public int getHeight(){
		return height;
	}

	/**Returns the number of columns of the world.
	 * @return the number of columns of the world.
	 */
	public int getWidth(){
		return width;
	}

	/**
	 * Create a task for each cell and assign the task to it.
	 * Sets all the tasks in the world as to visit.
	 */
	public void setUpForCoverage(){
		Cell cell;

		for(int i = 0; i < height; i++){
			for(int j = 0; j < width; j++){
				cell = map[i][j];
				Task task = new Task(cell, Task.Status.VISIT);
				cell.setTask(task);
			}
		}
	}


	/**
	 * Create a task for each cell that present weeds and assign the task to it.
	 * Sets all the task in the world as to spray
	 */
	public void setUpForWeed(){
		Cell cell;

		for(int i = 0; i < height; i++){
			for(int j = 0; j < width; j++){
				cell = map[i][j];
				if(cell.isWeed()){
					Task task = new Task(cell, Task.Status.SPRAY);
					cell.setTask(task);
				}
			}
		}
	}

	/**
	 * Adds weeds in Cells.
	 * @param n the number of cells that contain weeds
	 */
	public void addWeedCells(int n) {
		if(n>=height*width)
			throw new IllegalArgumentException("Too many weeds cells");

		for(int i=n;i>0;i--){
			int row=(int)(height*Math.random());
			int col=(int)(width*Math.random());

			if(!map[row][col].isWeed())
				map[row][col].setWeed(true);
			else
				i++;
		}
	}

	/**
	 * Clears current agents and adds the positions of the given ones to its own list.
	 * @param agentList the list of the agents, ordered for id from 1 to agentList.size().
	 */
	public void addAgents(List<Agent>agentList){
		this.agents = agentList;

		agentsCells = new ArrayList<Cell>(agentList.size());
		for(Agent a : agentList)
			agentsCells.add(a.getPosition());
	}

	// ********************************************* Action Execution ***************************

	/**
	 * Given an action, the agent is moved based on it.
	 * The agent internal state must be changed accordingly.
	 * <p> When calling this method, the world is notified the fact that the agent
	 * has a task associated to the task;
	 */
	public Task executeAction(int agId, Task agTask, Action act){
		System.out.println("[WORLD] agent id: " + agId + " action was: " + act);
		switch(act){
			case moveToLocation:
				return executeActionMoveToLocation(agId, agTask);
			case publishNextTask:
				return executeActionPublishNextTask(agId, agTask);
			case check:
				return executeActionCheck(agId, agTask);
			case spray:
				return executeActionSpray(agId, agTask);
			case noOp:
				break;
			default:
				throw new IllegalArgumentException("Unknown action: "+ act);
		}

		return null;
	}

	/**
	 * moves the agent a to Cell c associated with the task.
	 * Once c is reached the agent automatically update cell information:
	 * the task assigned to the cell is done and cells variables are updated.
	 *
	 * In general this one is the last action that an agent has to execute in each cycle, given a task
	 * (either a cell to visit or a cell to treat) this action moves the agent into position and
	 * acts as if the agent accomplished the task. i.e. reaching the cell is enough
	 *
	 * @param agId the id of the agent requesting to apply the action.
	 * @param agTask the task of the agent requesting to apply the action.
	 * @return the current task associated with the current cell
	 */
	private Task executeActionMoveToLocation(int agId, Task agTask){
		if(agTask.getCell().isVisited()){
			System.out.printf("ALREADY VISITED: [%d, %d]\n", agTask.getCell().getRow(), agTask.getCell().getCol());
		}
		this.setAgentPosition(agId, agTask.getCell());
		agTask.markAsComplete(agId);
		return agTask;
	}

	/**
	 * returns the task associated to the new position to spray or to visit (according to the exercise you choose).
	 * Compute next Task. The next Task is the next cell that has not been treated or visited
	 * in the grid and that can be seen as the task (i.e. where the agent has to spray).
	 * Cells that are already sprayed are skipped. If a next cell is found the world is
	 * updated with the new agent position. If there is no next cell null is returned.
	 *
	 *
	 * @param agId the id of the agent requesting to apply the action.
	 * @param agTask the task of the agent requesting to apply the action.
	 * @return the task
	 */
	private Task executeActionPublishNextTask(int agId, Task agTask){
		Task t;
		if(agTask == null || agTask.isDone()){
			int row=(int)(height*Math.random());
			int col=(int)(width*Math.random());
			t = new Task(new Cell(row, col), Task.Status.VISIT);
			System.out.print("[WORLD] [" + row + "; " + col + "] task assigned to: " + agId);
			System.out.println(" it was at [" + getAgentPosition(agId).getRow() + ", " + getAgentPosition(agId).getCol() + "]");
		} else {
			System.out.print("TODO: implement");
			t = new Task(new Cell(0, 0), Task.Status.VISIT);
		}
		return t;
	}

	/**
	 * Perfom the check operation over the current cell associated to the task in input.
	 * i.e. the robot scans the cell and mark it as visited, the task is marked as done
	 *
	 * @param agId the id of the agent requesting to apply the action.
	 * @param agTask the task of the agent requesting to apply the action.
	 * @return the task
	 */
	private Task executeActionCheck(int agId, Task agTask){
		if(agTask.getCell().isVisited()){
			System.out.print("WASTING TIME");
		}
		agTask.getCell().setVisited(true);
		agTask.markAsComplete(agId);
		System.out.printf("[WORLD] %d checked stuff at [%d, %d]\n", agId, agTask.getCell().getRow(), agTask.getCell().getCol());
		return agTask;
	}

	/**
	 * Perfom the spray operation over the current cell associated to the task in input.
	 * i.e. the robot spray the herbicidal on the cell and mark it as sprayed, the task is marked as done.
	 * If the cell was not visited it becomes visited.
	 *
	 * @param agId the id of the agent requesting to apply the action.
	 * @param agTask the task of the agent requesting to apply the action.
	 * @return the task
	 */
	private Task executeActionSpray(int agId, Task agTask){
		System.out.print("TODO: you should spray the herbicidal\n");
		return null;
	}

	// ************************************************ Communication ****************************

	/**
	 * =============================================================================
     * TODO Implement you own communication structure
     * Fell free to write any function needed by your implementation.
     * =============================================================================
	 */

	// ************************************************* Selectors to access the world components *******************

	/**Returns the number of agents in the world.
	 * @return the number of agents in the world.
	 */
	public int getNumAgents(){
		return agentsCells.size();
	}

	/**
	 * Returns the Cell with given coordinates.
	 * @param row the row of the Cell.
	 * @param col the column of the Cell.
	 * @return the Cell with given coordinates.
	 */
	public Cell getCell(int row, int col){
		return map[row][col];
	}

	/**
	 * Returns the occurrence of the Cell in the world according to the
	 * coordinates of the latter
	 * @param cell to be compared
	 * @return the World occurrence of the Cell with given coordinates.
	 */
	public Cell getCell(Cell cell){
		return this.getCell(cell.getRow(), cell.getCol());
	}

	/**
	 * Returns an Agent position.
	 * @param id the id of the agent.
	 * @return the Cell corresponding to the Agent position in the world.
	 */
	public Cell getAgentPosition(int id){
		return agentsCells.get(id-1);
	}

    /**
    * Returns all the agents in the given Location.
    * @param cell the Location to check.
    * @return list of all the id's of the agents in Location loc.
    */
    public List<Integer> getAgents(Cell cell){
        java.util.Iterator<Cell> it = agentsCells.listIterator();
        List<Integer> res = new LinkedList<Integer>();
        for(int id=1;it.hasNext();id++)
            if(it.next().equals(cell))
                res.add(id);
        return res;
    }

    /**
     * Returns all the agents in the Location with given coordinates.
     * @param row the row of the Location to check.
     * @param col the column of the Location to check.
     * @return list of all the id's of the agents in Location (row,col).
     */
     public List<Integer> getAgents(int row, int col){
         return getAgents(new Cell(row,col));
     }

	/**
	 * Sets an Agent position.
	 * @param id the id of the agent.
	 * @param c the Cell corresponding to the new Agent position in the world.
	 */
	public void setAgentPosition(int id,Cell c){
		agentsCells.set(id-1,c);
	}

	/**
	 * Returns true if the given location falls within the grid.
	 * @param row and col represent the location to check.
	 * @return true if the given location falls within the grid.
	 */
	public boolean isValid(int row, int col){
		return row>=0&&row<height&&col>=0&&col<width;
	}

	/**
	 * Scan the world to find all the uncompleted task. (e.g. non visited cells, untreated cells)
	 *
	 * @return all the tasks not accomplished in the current execution
	 */
	public LinkedList<Task> getUncompletedTask(){
		LinkedList<Task> uncTasks = new LinkedList<Task>();

		for(int i = 0; i < this.height; i++){
			for (int j = 0; j < this.width; j++){
				if(!this.map[i][j].getTask().isDone()){
					uncTasks.add(this.map[i][j].getTask());
				}
			}
		}
		return uncTasks;
	}

	// ************************************************ DCOP Central Agent ***************************/

	/**
	 * Method used to execute the DPOP procedure to solve the current problem.
	 * You have to fill it with your logic.
	 * You can use the given package multiagent.dpop, where you can find some basic implementations of
	 * the structure that you need to manage the problem. On the other hand, you can decide to implement
	 * your own solution.
	 *
	 * @return agent2tasks, a structure that map an agent to the task/s
	 */
	public HashMap<Integer,LinkedList<Task>> DPOPexecute(){
		return null;
	}
}
