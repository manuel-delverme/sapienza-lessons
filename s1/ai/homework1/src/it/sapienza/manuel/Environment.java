package it.sapienza.manuel;

import aima.core.agent.Action;

import java.util.*;

public class Environment {
	private final Position robot;
	private static Position goal;
	private static Position starting_position;
	private static final Set<Long> walls = new HashSet<>();
	static int optimal_RIGHT = 0;
    static int optimal_LEFT = 0;
	static int optimal_UP = 0;
	static int optimal_DOWN = 0;
	int taken_RIGHT = 0;
	int taken_LEFT = 0;
	int taken_UP = 0;
	int taken_DOWN = 0;

	public void update_path(Environment old_world, Action action) {
	}

	public enum taxicabAction implements Action {
		RIGHT,
		LEFT,
		UP,
		DOWN,;

		@Override
		public boolean isNoOp() {
			return false;
		}
	}

	boolean isEmpty(int x, int y) {
		long hash = ((long)x * Position.maxX) + y;
		return !walls.contains(hash);
	}

	Environment(Position robot) {
		this.robot = robot;
		int optimal_horizontal_moves = goal.x - starting_position.x;
		int optimal_vertical_moves = goal.y - starting_position.y;
		optimal_RIGHT = Math.max(optimal_horizontal_moves, 0);
		optimal_LEFT = Math.max(-optimal_horizontal_moves, 0);
		optimal_UP = Math.max(optimal_vertical_moves, 0);
		optimal_DOWN = Math.max(-optimal_vertical_moves, 0);
	}

	static void setStartingPosition(Position startingPosition) {
		starting_position = startingPosition;
	}
	static void setFinish(Position finish) {
		goal = finish;
	}

	static void addWall(Position position) {
		long hash = ((long)position.x * Position.maxX) + position.y;
		walls.add(hash);
	}

	Position getGoalPosition() {
		return goal;
	}

	Position getRobotPosition() {
		return robot;
	}
	Position getStartingPosition() {
		return starting_position;
	}

	@Override
	public int hashCode() {
		return this.robot.hashCode();
	}

	@Override
	public boolean equals(Object o) {
		return this.robot.equals(((Environment) o).getRobotPosition());
	}
}
