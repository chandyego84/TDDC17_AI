package searchCustom;

import java.util.Random;

public class CustomBreadthFirstSearch  extends CustomGraphSearch{

	public CustomBreadthFirstSearch(int maxDepth){
		// BFS -- FIFO -- insert nodes in the front of the frontier
		super(true); // Temporary random choice, you need to pick true or false!
		System.out.println("-->CUSTOM BREADTH FIRST SEARCH RUNNING<--");
		// System.out.println("Change line above in \"CustomBreadthFirstSearch.java\"!");
	}
};
