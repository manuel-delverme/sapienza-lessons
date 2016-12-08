package it.sapienza.manuel;

import aima.core.search.framework.HeuristicFunction;
class ManhattanHeuristics implements HeuristicFunction {

	public double h(Object state) {
		Environment world = (Environment) state;
		return gravityPull(world);
	}

	private int gravityPull(Environment board) {
		Position robotLocation = board.getRobotPosition();
		Position goalLocation = board.getGoalPosition();
		return robotLocation.distance_from(goalLocation);
	}
}
