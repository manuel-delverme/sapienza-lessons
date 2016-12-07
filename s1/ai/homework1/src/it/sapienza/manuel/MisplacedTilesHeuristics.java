package it.sapienza.manuel;

import aima.core.search.framework.HeuristicFunction;
import java.util.Map;

class MisplacedTilesHeuristics implements HeuristicFunction {
	private int[][] cost;

	MisplacedTilesHeuristics(int[][] occupancy){
		cost = new int[occupancy.length][occupancy[0].length];
		Position startingPosition = Environment.starting_position;
		Position goal = Environment.goal;

		int c_vert;
		int c_horiz;
		int c_vert_start = -startingPosition.y;
		int c_vert_goal = -goal.y;
		int c_horiz_start;
		int c_horiz_goal;
		for(int y=0; y < occupancy.length; y++){
			c_vert_start++;
			c_vert_goal++;
			c_vert = Math.min(Math.abs(c_vert_goal), Math.abs(c_vert_start));
			c_horiz_start = -startingPosition.x;
			c_horiz_goal = -goal.x;
			for(int x=0;  x < occupancy[0].length; x++){
				c_horiz_start++;
				c_horiz_goal++;
				c_horiz = Math.min(Math.abs(c_horiz_goal), Math.abs(c_horiz_start));
				cost[y][x] = c_horiz + c_vert;
			}
		}
	}

	public double h(Object state) {
		Environment world = (Environment) state;

	private int gravityPull(Environment board) {
		Position robotLocation = board.getRobotPosition();
		/*
		Position startingPosition = board.getStartingPosition();
		Map<Integer, Integer> optimal_path = Environment.getOptimalPath();

		int taken_horizontal_moves = robotLocation.x - startingPosition.x;
		int taken_vertical_moves = robotLocation.y - startingPosition.y;
		int taken_rights = Math.max(0, taken_horizontal_moves);
		int taken_lefts = Math.max(0, -taken_horizontal_moves);
		int taken_downs = Math.max(0, taken_vertical_moves);
		int taken_ups = Math.max(0, -taken_vertical_moves);
		int cost = 0;
		cost += Math.max(0, taken_rights - optimal_path.get(Environment.RIGHT));
		cost += Math.max(0, taken_lefts - optimal_path.get(Environment.LEFT));
		cost += Math.max(0, taken_downs - optimal_path.get(Environment.DOWN));
		cost += Math.max(0, taken_ups - optimal_path.get(Environment.UP));
		*/
		return cost[robotLocation.y][robotLocation.x];
	}
}
