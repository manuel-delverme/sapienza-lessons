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
		/*
		int real = robotLocation.distance_from(goalLocation);
		double myeur = 0.99 * robotLocation.distance_from(goalLocation);
		if (real != (int) Math.round(myeur)){
			System.out.println( "error " + real + " -> " + myeur);
		}
		*/
		// return (int) Math.round(0.99 * robotLocation.distance_from(goalLocation));
		return robotLocation.distance_from(goalLocation);
		// return (int) Math.sqrt(robotLocation.distance_from(goalLocation));
	}
}
