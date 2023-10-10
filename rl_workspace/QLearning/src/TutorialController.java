public class TutorialController extends Controller {

    public SpringObject object;

    ComposedSpringObject cso;

    /* These are the agents senses (inputs) */
	DoubleFeature x; /* Positions */
	DoubleFeature y;
	DoubleFeature vx; /* Velocities */
	DoubleFeature vy;
	DoubleFeature angle; /* Angle */

    /* Example:
     * x.getValue() returns the vertical position of the rocket 
     */

	/* These are the agents actuators (outputs)*/
	RocketEngine leftRocket;
	RocketEngine middleRocket;
	RocketEngine rightRocket;

    /* Example:
     * leftRocket.setBursting(true) turns on the left rocket 
     */
	
	public void init() {
		cso = (ComposedSpringObject) object;
		x = (DoubleFeature) cso.getObjectById("x");
		y = (DoubleFeature) cso.getObjectById("y");
		vx = (DoubleFeature) cso.getObjectById("vx");
		vy = (DoubleFeature) cso.getObjectById("vy");
		angle = (DoubleFeature) cso.getObjectById("angle");

		leftRocket = (RocketEngine) cso.getObjectById("rocket_engine_left");
		rightRocket = (RocketEngine) cso.getObjectById("rocket_engine_right");
		middleRocket = (RocketEngine) cso.getObjectById("rocket_engine_middle");
	}

    public void tick(int currentTime) {

    	/* TODO: Part 1, No. 5 */
    	// Implement the tick() method so that it receives readings from the sensors "angle", "vx", "vy" 
    	// and prints them out on the standard output
		Double vxValue = vx.getValue();
		Double vyValue = vy.getValue();
		Double angleValue = angle.getValue();
		
		// System.out.println("VX: " + vxValue);
		// System.out.println("VY: " + vyValue);
		System.out.println("Angle: " + angleValue);
		
		/*TODO: Part 1, No. 7*/
		// Set the rockets to fire or stop if "vy" or some other sensor falls below/above some threshold
		if (vxValue > 1) {
			// rocket stops if vx too high
			middleRocket.setBursting(false);
		}
    }

}
