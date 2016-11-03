package it.sapienza.manuel;

import aima.core.agent.Action;
import aima.core.environment.vacuum.VacuumEnvironment;
import aima.core.environment.vacuum.VacuumEnvironmentState;
import aima.core.search.framework.problem.ActionsFunction;
import aima.core.search.framework.problem.ResultFunction;

import java.util.LinkedHashSet;
import java.util.Set;

public class Result implements ResultFunction {

	public Environment result(Environment old_world, Action action) {

		Position old_robotLocation = old_world.getRobotPosition();
		Position new_robotLocation = old_robotLocation;
		if (action == Environment.Actions.RIGHT) {
			new_robotLocation = old_robotLocation.move_right();
		} else if (action == Environment.Actions.LEFT) {
			new_robotLocation = old_robotLocation.move_left();
		} else if (action == Environment.Actions.UP) {
			new_robotLocation = old_robotLocation.move_up();
		} else if (action == Environment.Actions.DOWN) {
			new_robotLocation = old_robotLocation.move_down();
		}
		Environment new_world = new Environment(new_robotLocation);
		return new_world;
	}

	@Override
	public Object result(Object s, Action a) {
		return result((Environment) s, a);
	}
}
