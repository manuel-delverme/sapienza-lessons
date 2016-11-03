package it.sapienza.manuel;

import java.util.HashSet;
import java.util.Set;

import aima.core.agent.Action;
import aima.core.agent.impl.DynamicAction;

public class Environment {
	private static int maxX;
	private static int maxY;
	private final Position robot;
	private static Position goal;
	private static final Set<Position> walls = new HashSet<>();
	enum Actions implements Action {
		UP, DOWN, RIGHT, LEFT;

		@Override
		public boolean isNoOp() {
			return false;
		}
	}

	boolean isEmpty(Position robotLocation) {
		return !walls.contains(robotLocation);
	}

	Environment(Position robot) {
		this.robot = robot;
	}

	static void setFinish(Position finish) {
		goal = finish;
	}

	static void addWall(Position position) {
		walls.add(position);
	}

	Position getGoalPosition() {
		return goal;
	}

	Position getRobotPosition() {
		return robot;
	}
}
