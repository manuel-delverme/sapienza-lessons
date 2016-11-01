package it.sapienza.manuel;

import aima.core.search.framework.problem.Problem;
import aima.core.environment.nqueens.NQueensBoard;
import aima.core.agent.Action;
import aima.core.agent.Agent;
import aima.core.search.framework.qsearch.GraphSearch;
import aima.core.search.framework.problem.Problem;
import aima.core.search.framework.Search;
import aima.core.search.framework.SearchAgent;
import aima.core.search.framework.qsearch.TreeSearch;
import aima.core.search.informed.AStarSearch;
import aima.core.search.uninformed.BreadthFirstSearch;
import aima.core.search.uninformed.DepthFirstSearch;
import aima.core.search.uninformed.IterativeDeepeningSearch;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.Math;

import static java.lang.Math.pow;

import java.util.List;
import java.util.StringTokenizer;

public class Main {
	public static void main(String[] args) throws Exception {
		Environment init = getEnvironment(args);

		//Use AIMA framework to solve the problem
		ActionFunction actFunc = new ActionFunction();
		Result resFunc = new Result();
		Goal goal = new Goal();
		Problem p = new Problem(init, actFunc, resFunc, goal);
		//TODO
		//store the path of the robot in the occupancy grid and save it in a bitmap image
		//
	}

	private static Environment getEnvironment(String[] parameters) throws IOException {
		//Input file must be specified in args[1]
		BufferedReader reader = new BufferedReader(new FileReader(new File(parameters[1])));

		//In order to increment the resolution of the grid we use v as the exponent of the power of 2;
		// so if v = 0 then m = 2^0 = 1 and the grid resolution is 16x16
		// if v = 1 then m = 2^1 = 2 and the grid resolution is 32x32
		//and so on...
		int v = Integer.parseInt(parameters[3]);
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
		System.out.println("X: " + robot.x() + " Y: " + robot.y());
		occupancy[robot.y()][robot.x()] = 255;
		tokens = new StringTokenizer(reader.readLine());
		Position finish = new Position(Integer.parseInt(tokens.nextToken()) * m, Integer.parseInt(tokens.nextToken()) * m);
		System.out.println("Goal");
		System.out.println("X: " + finish.x() + " Y: " + finish.y());
		occupancy[finish.y()][finish.y()] = 65280;

		//Build the environment
		Environment init = new Environment(robot);
		Environment.setFinish(finish);
		int numWalls = Integer.parseInt(reader.readLine());
		for (int i = 0; i < numWalls; i++) {
			tokens = new StringTokenizer(reader.readLine());
			Position temp = new Position(Integer.parseInt(tokens.nextToken()) * m, Integer.parseInt(tokens.nextToken()) * m);
			for (int x = 0; x < m; x++)
				for (int y = 0; y < m; y++) {
					int newX = temp.x() + x;
					int newY = temp.y() + y;
					Environment.addWall(new Position(newX, newY));
					occupancy[newY][newX] = 0x000000;
				}
		}

		//Store the occupancy matrix in a bitmap image
		new BMP().saveBMP(parameters[2], occupancy);
		return init;
	}
}
