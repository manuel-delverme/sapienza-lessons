package it.sapienza.manuel;

import aima.core.search.framework.problem.GoalTest;

class Goal implements GoalTest {
	@Override
	public boolean isGoalState(Object state) {
		Environment world = (Environment) state;
		return world.getRobotPosition().equals(world.getGoalPosition()) ;
	}
}
