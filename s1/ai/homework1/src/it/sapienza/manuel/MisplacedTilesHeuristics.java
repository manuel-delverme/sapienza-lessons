package it.sapienza.manuel;

import aima.core.agent.impl.DynamicAction;
import aima.core.search.framework.HeuristicFunction;

import java.util.Map;
import java.util.Set;

class MisplacedTilesHeuristics implements HeuristicFunction {

	public double h(Object state) {
		Environment world = (Environment) state;
		return gravityPull(world);
	}

	private int gravityPull(Environment board) {
		Position robotLocation = board.getRobotPosition();
		Position startingPosition = board.getStartingPosition();
		Map<Integer, Integer> optimal_path = Environment.getOptimalPath();

		int taken_horizontal_moves = robotLocation.x - startingPosition.x;
		int taken_vertical_moves = robotLocation.y - startingPosition.y;
		int taken_rights = Math.max(0, taken_horizontal_moves);
		int taken_lefts = Math.max(0, -taken_horizontal_moves);
		int taken_downs = Math.max(0, taken_vertical_moves);
		int taken_ups = Math.max(0, -taken_vertical_moves);
		int cost = 0;
		cost += Math.max(0, taken_rights - optimal_path.get(Environment.RIGHT));
		cost += Math.max(0, taken_lefts - optimal_path.get(Environment.LEFT));
		cost += Math.max(0, taken_downs - optimal_path.get(Environment.DOWN));
		cost += Math.max(0, taken_ups - optimal_path.get(Environment.UP));
		return cost;
	}
}
