package it.sapienza.manuel;

import aima.core.agent.Action;
import aima.core.agent.impl.DynamicAction;
import aima.core.search.framework.problem.ResultFunction;

public class Result implements ResultFunction {

	public Environment result(Environment old_world, DynamicAction action) {

		Position old_robotLocation = old_world.getRobotPosition();
		Position new_robotLocation = old_robotLocation;
		if (action.getName().equals("RIGHT")) {
			new_robotLocation = old_robotLocation.whats_right();
		} else if (action.getName().equals("LEFT")) {
			new_robotLocation = old_robotLocation.whats_left();
		} else if (action.getName().equals("UP")) {
			new_robotLocation = old_robotLocation.whats_above();
		} else if (action.getName().equals("DOWN")) {
			new_robotLocation = old_robotLocation.whats_below();
		}
		return new Environment(new_robotLocation);
	}

	@Override
	public Object result(Object s, Action a) {
		return result((Environment) s, (DynamicAction) a);
	}
}
