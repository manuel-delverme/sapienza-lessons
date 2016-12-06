package it.sapienza.manuel;

import java.util.*;

public class Environment {
	public static final Integer RIGHT = 1;
	public static final Integer LEFT = 2;
	public static final Integer DOWN = 3;
	public static final Integer UP = 4;
	private final Position robot;
	public static Position goal;
	public static Position starting_position;
	// private static final Set<Position> walls = new HashSet<>();
	private static final Set<Long> walls = new HashSet<>();

	private static final Map<Integer, Integer> optimal_path = new HashMap<>();
	private static Position startingPosition;

	// private static final HashMap<Integer, boolean[]> is_empty = null;
	static Map<Integer, Integer> getOptimalPath() {
		return optimal_path;
	}



	// boolean isEmpty(Position robotLocation) {
	boolean isEmpty(int x, int y) {
		// return !walls.contains(robotLocation);
		// return is_empty.get(robotLocation.y)[robotLocation.x];
		long hash = ((long)x * Position.maxX) + y;
		return !walls.contains(hash);
	}

	Environment(Position robot) {
		this.robot = robot;
		int optimal_horizontal_moves = goal.x - starting_position.x;
		int optimal_vertical_moves = goal.y - starting_position.y;
		optimal_path.put(Environment.RIGHT, Math.max(optimal_horizontal_moves, 0));
		optimal_path.put(Environment.LEFT, Math.max(-optimal_horizontal_moves, 0));
		optimal_path.put(Environment.UP, Math.max(optimal_vertical_moves, 0));
		optimal_path.put(Environment.DOWN, Math.max(-optimal_vertical_moves, 0));
	}

	static void setStartingPosition(Position startingPosition) {
		starting_position = startingPosition;
	}
	static void setFinish(Position finish) {
		goal = finish;
	}

	static void addWall(Position position) {
		// boolean[] row = is_empty.get(position.y);
		// row[position.x] = false;
		// is_empty.put(position.y, row);
		// walls.add(position);
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
