package it.sapienza.manuel;

import aima.core.search.framework.HeuristicFunction;
class GravityHeuristics implements HeuristicFunction {

	public double h(Object state) {
		Environment world = (Environment) state;
		return gravityPull(world);
	}

	private int gravityPull(Environment board) {
		Position robotLocation = board.getRobotPosition();
		Position goalLocation = board.getGoalPosition();
		int dist = robotLocation.distance_from(goalLocation);
		return dist*dist;
	}
}
