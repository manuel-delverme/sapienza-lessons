package it.sapienza.manuel;

import java.util.HashSet;
import java.util.Set;

public class Environment {
	private final Position robot;
	private static Position goal;
	// private static final Set<Position> walls = new HashSet<>();
	private static final Set<Long> walls = new HashSet<>();
	// private static final HashMap<Integer, boolean[]> is_empty = null;

	// boolean isEmpty(Position robotLocation) {
	boolean isEmpty(int x, int y) {
		// return !walls.contains(robotLocation);
		// return is_empty.get(robotLocation.y)[robotLocation.x];
		long hash = ((long)x * Position.maxX) + y;
		return !walls.contains(hash);
	}

	Environment(Position robot) {
		this.robot = robot;
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
		@Override
	public int hashCode() {
		return this.robot.hashCode();
	}

	@Override
	public boolean equals(Object o) {
		return this.robot.equals(((Environment) o).getRobotPosition());
	}
}
