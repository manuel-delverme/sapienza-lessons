package it.sapienza.manuel;

import aima.core.agent.Action;
import aima.core.search.framework.problem.ActionsFunction;
import aima.core.util.datastructure.XYLocation;

import java.util.HashSet;
import java.util.Set;

// a description of the possible actions available to the agent.
public class ActionFunction implements ActionsFunction {

	@Override
	public Set<Action> actions(Object state) {
		Environment world = (Environment) state;
		Set<Action> actions = new HashSet<>();
		Position location = world.getRobotPosition();

		if(location.x < Position.maxX) {
			Position new_location = new Position(location.x + 1, location.y);
			if(world.isEmpty(new_location)){
				actions.add(new RobotAction("RIGHT", new_location));
			}
		}
		if(location.x > 0) {
			Position new_location = new Position(location.x - 1, location.y);
			if(world.isEmpty(new_location)){
				actions.add(new RobotAction("LEFT", new_location));
			}
		}
		if(location.y > 0) {
			Position new_location = new Position(location.x, location.y + 1);
			if(world.isEmpty(new_location)){
				actions.add(new RobotAction("UP", new_location));
			}
		}
		if(location.y < Position.maxY) {
			Position new_location = new Position(location.x, location.y - 1);
			if(world.isEmpty(new_location)){
				actions.add(new RobotAction("DOWN", new_location));
			}
		}
		return actions;
	}
}
