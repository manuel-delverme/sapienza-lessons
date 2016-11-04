package it.sapienza.manuel;

class Position {
	static int maxX;
	static int maxY;
	int x;
	int y;

	Position(int xCoOrdinate, int yCoOrdinate){
		x = xCoOrdinate;
		y = yCoOrdinate;
	}

	Position move_down(){
		return new Position(x, y - 1);
	}

	Position move_up(){
		return new Position(x, y + 1);
	}

	Position move_right(){
		return new Position(x + 1, y);
	}

	Position move_left(){
		return new Position(x - 1, y);
	}

    @Override
    public String toString() {
        return "pos: (" + x + ", " + y + ")";
    }

	@Override
	public int hashCode() {
		return x*maxX + y;
	}

	@Override
	public boolean equals(Object o) {
		return o instanceof Position && o.hashCode() == hashCode();
	}

	public int distance_from(Position point2) {
		int x2 = point2.x;
		int y2 = point2.y;
		return (int) Math.sqrt((x-x2)*(x-x2) + (y-y2)*(y-y2));
	}
}
