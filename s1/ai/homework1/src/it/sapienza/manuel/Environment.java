package it.sapienza.manuel;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;

public class Environment {
	private static int maxX;
	private static int maxY;
	private final Position robot;
	private static Position goal;
	// private static final Set<Position> walls = new HashSet<>();
	private static final Set<Integer> walls_y = new HashSet<>();
	private static final Set<Integer> walls_x = new HashSet<>();
	// private static final HashMap<Integer, boolean[]> is_empty = null;

	// boolean isEmpty(Position robotLocation) {
	boolean isEmpty(int x, int y) {
		// return !walls.contains(robotLocation);
		// return is_empty.get(robotLocation.y)[robotLocation.x];
		return walls_x.contains(x) && walls_y.contains(y);
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
		walls_x.add(position.x);
		walls_y.add(position.y);
	}

	Position getGoalPosition() {
		return goal;
	}

	Position getRobotPosition() {
		return robot;
	}
}
