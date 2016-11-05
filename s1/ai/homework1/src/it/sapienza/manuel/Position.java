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

	Position whats_below(){
		return new Position(x, y - 1);
	}

	Position whats_above(){
		return new Position(x, y + 1);
	}

	Position whats_right(){
		return new Position(x + 1, y);
	}

	Position whats_left(){
		return new Position(x - 1, y);
	}

    @Override
    public String toString() {
        return "pos: (" + x + ", " + y + ")";
    }

	@Override
	public int hashCode() {
		return (x << 4) + y;
	}

	@Override
	public boolean equals(Object o) {
		return o instanceof Position && o.hashCode() == hashCode();
	}

	public int distance_from(Position point2) {
		int x2 = point2.x;
		int y2 = point2.y;
		return Math.abs(x-x2) + Math.abs(y-y2);
	}
}
