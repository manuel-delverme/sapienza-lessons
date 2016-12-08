package it.sapienza.manuel;

import aima.core.agent.Action;
import aima.core.search.framework.problem.ActionsFunction;

import java.util.HashSet;
import java.util.Set;

// a description of the possible actions available to the agent.
class ActionFunction implements ActionsFunction {

	@Override
	public Set<Action> actions(Object state) {
		Environment world = (Environment) state;
		Position location = world.getRobotPosition();
		Set<Action> actions = new HashSet<>();

		if(location.x > 0) {
			if(world.isEmpty(location.x - 1, location.y)){
				actions.add(Environment.taxicabAction.LEFT);
			}
		}
		if(location.y < Position.maxY) {
			if(world.isEmpty(location.x, location.y + 1)){
				actions.add(Environment.taxicabAction.UP);
			}
		}
		if(location.x < Position.maxX) {
			if(world.isEmpty(location.x + 1, location.y)){
				actions.add(Environment.taxicabAction.RIGHT);
			}
		}
		if(location.y > 0) {
			if(world.isEmpty(location.x, location.y - 1)){
				actions.add(Environment.taxicabAction.DOWN);
			}
		}
		return actions;
	}
}
