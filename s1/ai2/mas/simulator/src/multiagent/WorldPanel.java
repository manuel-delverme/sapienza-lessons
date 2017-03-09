package multiagent;

import multiagent.dpop.DepthTree;

import java.awt.*;
import java.awt.event.*;

import javax.swing.*;

/**
 * This class is used to display graphically the state of the world.
 * <p> When pressing any button on the keyboard, the simulation stops or restarts.
 *
 * @author Albani Dario
 * @author Federico Patota
 * @author Gabriele Buondonno
 * @version 1.0 - May 22, 2013
 */
public class WorldPanel extends JPanel implements ActionListener, KeyListener {
	private static final long serialVersionUID = 1L;
	/**
	 * Simulator.
	 */
	private AgentSim simulator;
	/**
	 * When this Timer fires an ActionEvent, a new step is
	 * performed and the panel is repainted.
	 */
	private Timer timer;
	/**
	 * Dimension of one cell in pixels.
	 */
	private int dim = 40;

	/**
	 * Constructor for this class.
	 *
	 * @param sim the simulator.
	 * @param ms  time interval between two frames, in milliseconds.
	 */
	public WorldPanel(AgentSim sim, int ms) {
		this.simulator = sim;
		World world = simulator.world;

		setPreferredSize(new Dimension(world.getWidth() * dim, world.getHeight() * dim));
		timer = new Timer(ms, this);
	}

	/**
	 * Creates a new WorldPanel with a new AgentSim and a new World.
	 * A frame is created to contain the panel, which is registered as a KeyListener for it.
	 * The scene is displayed.
	 */
	public static void main(String[] args) throws Exception {
		//simulation parameters:
		int rows = 12;
		int columns = 12;
		int weedCells = 20;
		int agents = 4;

		//creating simulator with a new world
		AgentSim sim = new AgentSim(rows, columns, weedCells, agents);

		//storing world data
		//sim.storeWorld("world.mas");

		//creating simulator with a loaded world
		//AgentSim sim=new AgentSim("world.mas",agents,initialTasks);

		//creating WorldPanel

		WorldPanel panel = new WorldPanel(sim, 20);

		//creating and setting frame
		JFrame frame = new JFrame("World");
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frame.setContentPane(panel);
		frame.pack();
		frame.setResizable(false);

		//registering the panel as a KeyListener for the frame
		frame.addKeyListener(panel);

		//displaying scene
		frame.setVisible(true);
	}

	/**
	 * Displays the scene.
	 */
	public void paintComponent(Graphics g) {
		if (simulator == null) {
			return;
		}
		World world = simulator.world;
		for (int row = 0; row < world.getHeight(); row++) {
			for (int col = 0; col < world.getWidth(); col++) {
				Cell cell = world.getCell(row, col);
				if (cell.isVisited()) {
					// System.out.println(cell.getCol() + ", " + cell.getRow() + " is visited: RED");
					g.setColor(Color.RED);
				} else if (cell.isWeed()) {
					// System.out.println(cell.getCol() + ", " + cell.getRow() + " is weed: GREEN");
					g.setColor(Color.GREEN);
				} else {
					g.setColor(Color.WHITE);
				}
				g.fillRect(col * dim, row * dim, dim, dim);
				g.drawRect(col * dim, row * dim, dim, dim);

				java.util.List<Integer> agents = world.getAgents(row, col);
				int numAg = agents.size();
				if (numAg != 0) {
					g.setColor(Color.YELLOW);
					g.fillOval(col * dim + 1, row * dim + 1, dim - 2, dim - 2);

					g.setColor(Color.BLACK);
					StringBuilder builder = new StringBuilder();
					for (Integer a : agents) {
						builder.append(a);
						builder.append(',');
					}
					builder.deleteCharAt(builder.length() - 1);
					String string = builder.toString();

					int fontDivider = string.length() - numAg + 1;
					Font font = g.getFont().deriveFont(((float) dim) / fontDivider);
					g.setFont(font);
					FontMetrics metrics = g.getFontMetrics(font);
					int stringW = metrics.stringWidth(string);
					int stringH = metrics.getAscent() - metrics.getDescent();
					g.drawString(string, col * dim + (dim - stringW) / 2, row * dim + (stringH + dim) / 2);
				}
			}
		}
	}

	/**
	 * Method overridden to have immediate refresh of the scene.
	 */
	public void repaint() {
		Graphics g = getGraphics();
		if (g != null)
			paintComponent(g);
		else
			super.repaint();
	}

	/**
	 * Performs a new step and repaints the panel.
	 * If doOneStep() returns true, the simulation is stopped
	 * and a message dialog is displayed.
	 */
	public void actionPerformed(ActionEvent evt) {
		if (evt.getSource() == timer) {
			boolean stop = false;
			try {
				stop = simulator.doOneStep();
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			if (stop) {
				timer.stop();
				JOptionPane.showMessageDialog(null, "Simulation is over!\n\n" + simulator.statsToString());
				return;
			}
			repaint();
		}
	}

	/**
	 * Stops or restarts the simulation when any key is pressed.
	 */
	public void keyPressed(KeyEvent evt) {
		if (timer.isRunning()) timer.stop();
		else timer.start();
	}

	/**
	 * Doesn't do anything, needed for implementing KeyListener.
	 */
	public void keyReleased(KeyEvent evt) {
	}

	/**
	 * Doesn't do anything, needed for implementing KeyListener.
	 */
	public void keyTyped(KeyEvent evt) {
	}

	/**
	 * Changes the time interval between two frames.
	 *
	 * @param ms time interval, in milliseconds.
	 */
	public void setTimeDelay(int ms) {
		timer.setDelay(ms);
	}
}
