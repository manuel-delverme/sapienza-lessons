package it.sapienza.manuel;

import java.util.HashSet;
import java.util.Set;

import aima.core.agent.Agent;
import aima.core.environment.nqueens.NQueensGoalTest
import aima.core.environment.map.MapAgent;
import aima.core.environment.xyenv.XYEnvironment;
import aima.core.environment.xyenv.Wall;
import aima.core.util.datastructure.XYLocation;

class Environment extends XYEnvironment {
	private static int maxX;
	private static int maxY;
	private final Position robot;
	private static Position goal;
	private static Set<Position> walls = new HashSet<>();

	Environment(Position robot) {
		super(maxX, maxY);
		for(Position position : walls)
			this.addObjectToLocation(new Wall(), position);
		this.robot = robot;
		// Agent a = new MapAgent();
		// this.addAgent(a);
	}

	static void setFinish(Position finish) {
		goal = finish;
	}

	static void addWall(Position position) {
		walls.add(position);
	}

	public static Position getGoal() {
		return goal;
	}

	public Position getRobot() {
		return robot;
	}

	//TODO
	//insert the required class methods
	//
}
