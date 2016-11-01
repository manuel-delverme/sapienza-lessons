package it.sapienza.manuel;
import aima.core.util.datastructure.XYLocation;

public class Position extends XYLocation {
	static int maxX;
	static int maxY;

	Position(int xCoOrdinate, int yCoOrdinate){
		super(xCoOrdinate, yCoOrdinate);
	}

	public Position left(){
		if(getYCoOrdinate()-1 > 0){
			return new Position (getXCoOrdinate(), getYCoOrdinate()-1);
		}
		return null;
	}

	public Position down(){
		if(getXCoOrdinate()+1 <= maxX){
			return new Position (getXCoOrdinate()+1, getYCoOrdinate());
		}
		return null;
	}

	public Position right(){
		if(getYCoOrdinate()+1 <= maxY){
			return new Position (getXCoOrdinate(), getYCoOrdinate()+1);
		}
		return null;
	}

	public Position up(){
		if(getXCoOrdinate()-1 > 0){
			return new Position (getXCoOrdinate()-1, getYCoOrdinate());
		}
		return null;
	}

    @Override
    public String toString() {
        return "pos: (" + getXCoOrdinate() + ", " + getYCoOrdinate() + ")";
    }

	public int x() {
		return getXCoOrdinate();
	}
	public int y() {
		return getYCoOrdinate();
	}
}
