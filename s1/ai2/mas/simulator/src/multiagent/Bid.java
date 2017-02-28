package multiagent;

/**
 * This class represents a bid an Agent can make, given an available task.
 * The task is represented by a Cell.
 *
 * @author Albani Dario
 * @author Federico Patota
 * @author Gabriele Buondonno
 * @version 1.0 - May 22, 2013
 */
public class Bid {

	/**
	 * This boolean represents the intention of the Agent to participate to the auction.
	 * If it is true, the Agent is interested, otherwise it's not.
	 */
	public final boolean isPropose;

	/**
	 * The task associated with the cell.
	 */
	public final Task task;

	/**
	 * The estimated cost of reaching the given task for the Agent making this Bid.
	 */
	public final int cost;

	/**
	 * The Agent making this Bid.
	 */
	public final Agent bidder;

	public Bid(boolean isPropose, Task task, int cost, Agent bidder) {
		this.isPropose = isPropose;
		this.task = task;
		this.cost = cost;
		this.bidder = bidder;
	}
}
