```
import java.util.*;
import processing.core.PApplet;

/* GAME RULE 
 * The game is over when the head of the snake hits an edge of the map or one of the sections.
 * The goal of the game is to make the snake as long as possible.
 * */

public class Snake extends PApplet {
	private MySnake ms;
	private Food food;
	boolean game = true;
	int gameSpeed=10;
	int gs_tmp;
	boolean gameLoop = false;
	
	/* My snake class */
	class MySnake {
		private ArrayList<Pos> pos;
		private Pos dir;
		int eatNum;

		public MySnake() {
			pos = new ArrayList<>();
			dir = new Pos(20, 0); // default east
			// default. 4 cell of snake
			for (int i = 0; i < 4; i++)
				pos.add(new Pos((width / 2 - (width / 2) % 20) + i * 20, height / 2 - (height / 2 % 20))); // default position
		}
	}

	/* Food class */
	class Food {
		private Pos pos;
		private Random r;

		public Food() {
			r = new Random();
			pos = new Pos(r.nextInt(((width) / 20)) * 20, r.nextInt(((height) / 20)) * 20); // 20~width-20,
																									// 20~height-20(+=20)
		}

		public void setFoodPos() {
			boolean checkPos=false;
			int x;
			int y;
			do {
				x = r.nextInt(((width) / 20)) * 20;
				y = r.nextInt(((height) / 20)) * 20;
				for(int i=0;i<ms.pos.size();i++)
					if (ms.pos.get(i).posX != x && ms.pos.get(i).posY != y)
						checkPos=false;
					else {
						checkPos=true;
						break;
					}
			} while (!checkPos);
			this.pos.posX = x;
			this.pos.posY = y;
			//System.out.println("posX:"+x+"posY"+y);
		}
	}

	/* Position class(2D) */
	class Pos {
		private int posX;
		private int posY;

		public Pos(int x, int y) {
			this.posX = x;
			this.posY = y;
		}
	}

	/* screen size setting */
	public void settings() {
		//fullScreen();
		size(1000,800);
	}

	public void setup() {
		ms = new MySnake();
		food = new Food();
	}

	public void draw() {
		if (game) {
			frameRate(gameSpeed);
			/* background & line draw */
			background(0);
			stroke(255, 50);
			for (int i = 0; i < width; i += 20)
				line(i, 0, i, height);
			for (int j = 0; j < height; j += 20)
				line(0, j, width, j);

			/* MySnake */	
			fill(163, 73, 164, 200); // purple color
			ms.pos.add(new Pos(ms.pos.get(ms.pos.size() - 1).posX + ms.dir.posX,
					ms.pos.get(ms.pos.size() - 1).posY + ms.dir.posY)); // add new pos

			if (checkEat())
				ms.pos.add(new Pos(ms.pos.get(ms.pos.size() - 1).posX + ms.dir.posX,
						ms.pos.get(ms.pos.size() - 1).posY + ms.dir.posY)); // add new pos
			ms.pos.remove(0);

			for (int i = 0; i < ms.pos.size(); i++) {
				if(i==ms.pos.size()-1) {	//head section
					fill(100,100,200);
					rect(ms.pos.get(i).posX, ms.pos.get(i).posY, 20, 20);
				}
				else 
					rect(ms.pos.get(i).posX, ms.pos.get(i).posY, 20, 20);
			}

			/* food */
			fill(209, 29, 33, 255);
			rect(food.pos.posX, food.pos.posY, 20, 20);

			/* Check if my snake die */
			if (checkDie()) {
				game = false;
				ms.pos.clear();
				background(0);
				textAlign(CENTER);
				fill(255, 255, 255);
				textSize(30);
				text("You Die!\nPress <X> to exit.\nYou eat " + ms.eatNum + "!\nPress <R> to regame.", width / 2,
						height / 2);
			}
		} else {
			if (keyCode == 'R') {
				reset();
			}
		}
	}

	public boolean checkEat() {
		if (ms.pos.get(ms.pos.size() - 1).posX == food.pos.posX
				&& ms.pos.get(ms.pos.size() - 1).posY == food.pos.posY) {
			food.setFoodPos();
			ms.eatNum++;
			gameSpeed=10+ms.pos.size();
			return true;
		}
		return false;
	}

	public boolean checkDie() {
		/* check if my snake is out of screen */
		if (ms.pos.get(ms.pos.size() - 1).posX < 0 || ms.pos.get(ms.pos.size() - 1).posY < 0
				|| ms.pos.get(ms.pos.size() - 1).posX > width || ms.pos.get(ms.pos.size() - 1).posY > height)
			return true;

		/* check if my snake hit itself. */
		for (int i = 0; i < ms.pos.size() - 1; i++)
			if (ms.pos.get(ms.pos.size() - 1).posX == ms.pos.get(i).posX
					&& ms.pos.get(ms.pos.size() - 1).posY == ms.pos.get(i).posY)
				return true;
		return false;
	}

	public void keyPressed() {
		if (keyCode == RIGHT&&game) {
			if (ms.dir.posX != -20) {
				ms.dir.posX = 20;
				ms.dir.posY = 0;
			}
		} else if (keyCode == LEFT&&game) {
			if (ms.dir.posX != 20) {
				ms.dir.posX = -20;
				ms.dir.posY = 0;
			}
		} else if (keyCode == DOWN&&game) {
			if (ms.dir.posY != -20) {
				ms.dir.posX = 0;
				ms.dir.posY = 20;
			}
		} else if (keyCode == UP&&game) {
			if (ms.dir.posY != 20) {
				ms.dir.posX = 0;
				ms.dir.posY = -20;
			}
		}
		else if (keyCode == 'P') {	//pause
			if(!gameLoop&&game) {
				gameLoop=true;
				textAlign(CENTER);
				fill(255, 255, 255);
				textSize(30);
				text("Press <P> for start!", width / 2,
						height / 2);
				noLoop();
			}
			else {
				gameLoop=false;
				loop();
			}
		}
		else if (keyCode ==' '&&game) {
			if(gameSpeed<60) {
				gs_tmp=gameSpeed;
				gameSpeed=60;
			}
		}
		else if (keyCode =='X'&&!game) {
			exit();
		}
	}
	public void keyReleased() {
		if(keyCode ==' '&&game)
			gameSpeed = gs_tmp;
	}
	public void reset() {
		game = true;
		gameSpeed=10;
		ms = new MySnake();
	}

	/* main method */
	public static void main(String args[]) {
		PApplet.main("Snake");
	}

}
```
