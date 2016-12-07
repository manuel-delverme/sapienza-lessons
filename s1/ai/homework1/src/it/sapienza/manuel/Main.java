package it.sapienza.manuel;

import aima.core.agent.Action;
import aima.core.agent.EnvironmentObject;
import aima.core.search.framework.problem.Problem;
import aima.core.search.framework.qsearch.GraphSearch;
import aima.core.search.framework.SearchAgent;
import aima.core.search.informed.AStarSearch;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;

import static java.lang.Math.pow;

import java.util.StringTokenizer;

public class Main {
	public static void main(String[] args) throws Exception {
		// the initial state that the agent starts in.
		//Input file must be specified in args[1]
		BufferedReader reader = new BufferedReader(new FileReader(new File(args[1])));
		//In order to increment the resolution of the grid we use v as the exponent of the power of 2;
		// so if v = 0 then m = 2^0 = 1 and the grid resolution is 16x16
		// if v = 1 then m = 2^1 = 2 and the grid resolution is 32x32
		//and so on...
		int v = Integer.parseInt(args[3]);
		int m = (int) pow(2, v);
		System.out.println("M: " + m);

		//Read from the file and set the grid dimensions
		StringTokenizer tokens = new StringTokenizer(reader.readLine());
		int maxX = Integer.parseInt(tokens.nextToken()) * m;
		int maxY = Integer.parseInt(tokens.nextToken()) * m;
		System.out.println("maxX: " + maxX + " maxY: " + maxY);
		Position.maxX = maxX;
		Position.maxY = maxY;

		//Store the matrix of integers that will be written in the .bmp file
		//and initialize it with white cells
		int[][] occupancy = new int[maxX][maxY];
		for (int i = 0; i < maxX; i++)
			for (int j = 0; j < maxY; j++)
				occupancy[i][j] = 16777215;

		//Read from the file the start and the goal position
		//and store them in the occupancy matrix
		tokens = new StringTokenizer(reader.readLine());
		Position robot = new Position(Integer.parseInt(tokens.nextToken()) * m, Integer.parseInt(tokens.nextToken()) * m);
		System.out.println("Robot");
		System.out.println("X: " + robot.x + " Y: " + robot.y);
		occupancy[robot.y][robot.x] = 255;
		tokens = new StringTokenizer(reader.readLine());
		Position finish = new Position(Integer.parseInt(tokens.nextToken()) * m, Integer.parseInt(tokens.nextToken()) * m);
		System.out.println("Goal");
		System.out.println("X: " + finish.x + " Y: " + finish.y);
		occupancy[finish.y][finish.x] = 65280;

		//Build the environment
		Environment.setFinish(finish);
		Environment.setStartingPosition(robot);
		Environment init = new Environment(robot);
		int numWalls = Integer.parseInt(reader.readLine());
		for (int i = 0; i < numWalls; i++) {
			tokens = new StringTokenizer(reader.readLine());
			Position temp = new Position(Integer.parseInt(tokens.nextToken()) * m, Integer.parseInt(tokens.nextToken()) * m);
			for (int x = 0; x < m; x++)
				for (int y = 0; y < m; y++) {
					int newX = temp.x + x;
					int newY = temp.y + y;
					Environment.addWall(new Position(newX, newY));
					occupancy[newY][newX] = 0x000000;
				}
		}

		//Store the occupancy matrix in a bitmap image
		new BMP().saveBMP(args[2], occupancy);

		// a description of the possible actions available to the agent.
		ActionFunction actFunc = new ActionFunction();

		// a description of what each action does; the formal name for
		// this is the transition model, specified by a function
		// RESULT(s, a) that returns the state that results from doing
		// action a in state s.
		Result resFunc = new Result();
		Result resMisplacedFunc = new ResultMisplaced();

	    // test determines whether a given state is a goal state.
		Goal goal = new Goal();
		Problem p; //, (s, a, sDelta) -> 10);
		p = new Problem(init, actFunc, resFunc, goal);

		// DepthFirstSearch search = new DepthFirstSearch(new GraphSearch());
		System.out.println("manhattan heuristics:");
		p = new Problem(init, actFunc, resFunc, goal);
		AStarSearch search = new AStarSearch(new GraphSearch(), new ManhattanHeuristics());
		long startTime;
		long endTime;
		long manhattan_time;
		SearchAgent agent = null;
		startTime = System.currentTimeMillis();
		for(int i = 0; i < 0; i++){
			agent = new SearchAgent(p,search);
		}
		endTime = System.currentTimeMillis();
		manhattan_time = endTime - startTime;
		System.out.println("Time: " + manhattan_time + " millisecond");
		// System.out.println(agent.getInstrumentation());

		System.out.println("misplaced heuristics:");
		p = new Problem(init, actFunc, resMisplacedFunc, goal);
		search = new AStarSearch(new GraphSearch(), new MisplacedTilesHeuristics());
		startTime = System.currentTimeMillis();
		for(int i = 0; i < 1; i++){
			agent = new SearchAgent(p,search);
		}
		endTime = System.currentTimeMillis();
		System.out.println(agent.getInstrumentation());
		float misplaced_time = endTime - startTime;
		System.out.println("Time: " + misplaced_time + " millisecond");
		System.out.println("misplaced tiles is: " + manhattan_time / misplaced_time + " times faster");
		/*
		List<Action> listAct = agent.getActions();
		System.out.println("length: " + listAct.size());
		listAct.remove(listAct.size() - 1);
		int robot_x = finish.x;
		int robot_y = finish.y;
		for(Action action : listAct){
			System.out.println("PATH: " + action.toString());
			if (action == Environment.taxicabAction.RIGHT) {
				robot_x -= 1;
			} else if (action == Environment.taxicabAction.LEFT) {
				robot_x += 1;
			} else if (action == Environment.taxicabAction.UP) {
				robot_y += 1;
			} else if (action == Environment.taxicabAction.DOWN) {
				robot_y -= 1;
			}
			occupancy[robot_x][robot_y] = 0xFF0000;
		}
		*/

		new BMP().saveBMP(args[2], occupancy);
	}

	private static class ResultMisplaced extends Result {
		public Object result(Object s, Action action) {
			Environment old_world = (Environment) s;
			Environment new_world = coreResult(s, action);
			new_world.taken_RIGHT = old_world.taken_RIGHT;
			new_world.taken_LEFT = old_world.taken_LEFT;
			new_world.taken_DOWN = old_world.taken_DOWN;
			new_world.taken_UP = old_world.taken_UP;
			if (action == Environment.taxicabAction.RIGHT) {
				new_world.taken_RIGHT = old_world.taken_RIGHT + 1;
			} else if (action == Environment.taxicabAction.LEFT) {
				new_world.taken_LEFT = old_world.taken_LEFT + 1;
			} else if (action == Environment.taxicabAction.UP) {
				new_world.taken_UP = old_world.taken_UP + 1;
			} else if (action == Environment.taxicabAction.DOWN) {
				new_world.taken_DOWN = old_world.taken_DOWN + 1;
			}
			return new_world;

		}
	}
}
