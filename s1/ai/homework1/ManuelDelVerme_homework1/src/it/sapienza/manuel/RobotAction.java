package it.sapienza.manuel;

import aima.core.agent.impl.DynamicAction;

public class RobotAction extends DynamicAction{
	Position endpoint;

	public RobotAction(String name, Position endpoint) {
		super(name);
		this.endpoint = endpoint;
	}

	@Override
	public boolean isNoOp() {
		return false;
	}
}
