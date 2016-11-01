package it.sapienza.manuel;

import aima.core.search.framework.problem.GoalTest;

public class Goal implements GoalTest {
	@Override
	public boolean isGoalState(Object state) {
		return board.getNumberOfQueensOnBoard() == board.getSize()
				&& board.getNumberOfAttackingPairs() == 0;
	}
	public boolean isGoalState(Object state) {
		Environment world = (Environment) state;
		return world.getRobotLocation() == world.getGoalLocation();
	}
}
