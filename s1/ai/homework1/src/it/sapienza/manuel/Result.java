package it.sapienza.manuel;

import aima.core.agent.Action;
import aima.core.agent.impl.DynamicAction;
import aima.core.environment.vacuum.VacuumEnvironment;
import aima.core.environment.vacuum.VacuumEnvironmentState;
import aima.core.search.framework.problem.ActionsFunction;
import aima.core.search.framework.problem.ResultFunction;

import java.util.LinkedHashSet;
import java.util.Set;

public class Result implements ResultFunction {

	public Environment result(Environment old_world, DynamicAction action) {

		Position old_robotLocation = old_world.getRobotPosition();
		Position new_robotLocation = old_robotLocation;
		if (action.getName() == "RIGHT") {
			new_robotLocation = old_robotLocation.move_right();
		} else if (action.getName() == "LEFT") {
			new_robotLocation = old_robotLocation.move_left();
		} else if (action.getName() == "UP") {
			new_robotLocation = old_robotLocation.move_up();
		} else if (action.getName() == "DOWN") {
			new_robotLocation = old_robotLocation.move_down();
		}
		return new Environment(new_robotLocation);
	}

	@Override
	public Object result(Object s, Action a) {
		return result((Environment) s, (DynamicAction) a);
	}
}
