package it.sapienza.manuel;

import aima.core.agent.impl.DynamicAction;
import aima.core.search.framework.HeuristicFunction;

import java.util.Map;
import java.util.Set;

class MisplacedTilesHeuristics implements HeuristicFunction {

	public double h(Object state) {
		Environment world = (Environment) state;

		int cost = 0;
		cost += Math.max(0, world.taken_RIGHT - Environment.optimal_RIGHT);
		cost += Math.max(0, world.taken_LEFT - Environment.optimal_LEFT);
		cost += Math.max(0, world.taken_DOWN - Environment.optimal_DOWN);
		cost += Math.max(0, world.taken_UP - Environment.optimal_UP);
		return cost;
	}
}
