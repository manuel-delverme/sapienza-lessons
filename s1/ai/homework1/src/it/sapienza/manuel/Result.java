package it.sapienza.manuel;

import aima.core.agent.Action;
import aima.core.search.framework.problem.ResultFunction;

public class Result implements ResultFunction {

	public Environment coreResult(Object s, Action action) {
		Environment old_world = (Environment) s;
		Position old_robotLocation = old_world.getRobotPosition();
		Position new_robotLocation = old_robotLocation;
		if (action == Environment.taxicabAction.RIGHT) {
			new_robotLocation = old_robotLocation.whats_right();
		} else if (action == Environment.taxicabAction.LEFT) {
			new_robotLocation = old_robotLocation.whats_left();
		} else if (action == Environment.taxicabAction.UP) {
			new_robotLocation = old_robotLocation.whats_above();
		} else if (action == Environment.taxicabAction.DOWN) {
			new_robotLocation = old_robotLocation.whats_below();
		}
		return new Environment(new_robotLocation);
	}
	@Override
	public Object result(Object s, Action action) {
		return coreResult(s, action);
	}
}
