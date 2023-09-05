from lab1.liuvacuum import *

DEBUG_OPT_DENSEWORLDMAP = False

AGENT_STATE_UNKNOWN = 0
AGENT_STATE_WALL = 1
AGENT_STATE_CLEAR = 2
AGENT_STATE_DIRT = 3
AGENT_STATE_HOME = 4

AGENT_DIRECTION_NORTH = 0
AGENT_DIRECTION_EAST = 1
AGENT_DIRECTION_SOUTH = 2
AGENT_DIRECTION_WEST = 3


def direction_to_string(cdr):
    cdr %= 4
    return "NORTH" if cdr == AGENT_DIRECTION_NORTH else\
        "EAST" if cdr == AGENT_DIRECTION_EAST else\
        "SOUTH" if cdr == AGENT_DIRECTION_SOUTH else\
        "WEST"  # if dir == AGENT_DIRECTION_WEST


"""
Internal state of a vacuum agent
"""
class MyAgentState:

    def __init__(self, width, height):

        # Initialize perceived world state
        self.world = [[AGENT_STATE_UNKNOWN for _ in range(height)] for _ in range(width)]
        self.world[1][1] = AGENT_STATE_HOME

        # Agent internal state
        self.last_action = ACTION_NOP
        self.direction = AGENT_DIRECTION_EAST
        self.pos_x = 1
        self.pos_y = 1
        ### DFS VARIABLES FOR TRAVERSING THE GRID ###
        self.home_found = False
        # Direction stack indicates directions taken by agent
        # Home stack indicates directions taken by agent since home was found
            # Used to trace back how to return back home
        self.direction_stack = []
        self.direction_home_stack = []


        # Metadata
        self.world_width = width
        self.world_height = height

    """
    Update perceived agent location
    """

    def update_position(self, bump):
        if not bump and self.last_action == ACTION_FORWARD:
            if self.direction == AGENT_DIRECTION_EAST:
                self.pos_x += 1
            elif self.direction == AGENT_DIRECTION_SOUTH:
                self.pos_y += 1
            elif self.direction == AGENT_DIRECTION_WEST:
                self.pos_x -= 1
            elif self.direction == AGENT_DIRECTION_NORTH:
                self.pos_y -= 1

    """
    Update perceived or inferred information about a part of the world
    """

    def update_world(self, x, y, info):
        self.world[x][y] = info

    """
    Dumps a map of the world as the agent knows it
    """

    def print_world_debug(self):
        for y in range(self.world_height):
            for x in range(self.world_width):
                if self.world[x][y] == AGENT_STATE_UNKNOWN:
                    print("?" if DEBUG_OPT_DENSEWORLDMAP else " ? ", end="")
                elif self.world[x][y] == AGENT_STATE_WALL:
                    print("#" if DEBUG_OPT_DENSEWORLDMAP else " # ", end="")
                elif self.world[x][y] == AGENT_STATE_CLEAR:
                    print("." if DEBUG_OPT_DENSEWORLDMAP else " . ", end="")
                elif self.world[x][y] == AGENT_STATE_DIRT:
                    print("D" if DEBUG_OPT_DENSEWORLDMAP else " D ", end="")
                elif self.world[x][y] == AGENT_STATE_HOME:
                    print("H" if DEBUG_OPT_DENSEWORLDMAP else " H ", end="")

            print()  # Newline
        print()  # Delimiter post-print


"""
Vacuum agent
"""
class MyVacuumAgent(Agent):

    def __init__(self, world_width, world_height, log):
        super().__init__(self.execute)
        self.initial_random_actions = 10
        self.iteration_counter = world_width * world_width * 4
        self.state = MyAgentState(world_width, world_height)
        self.log = log

    def move_to_random_start_position(self, bump):
        action = random()

        self.initial_random_actions -= 1
        self.state.update_position(bump)

        if action < 0.1666666:   # 1/6 chance
            self.state.direction = (self.state.direction + 3) % 4
            self.state.last_action = ACTION_TURN_LEFT
            return ACTION_TURN_LEFT
        elif action < 0.3333333:  # 1/6 chance
            self.state.direction = (self.state.direction + 1) % 4
            self.state.last_action = ACTION_TURN_RIGHT
            return ACTION_TURN_RIGHT
        else:                    # 4/6 chance
            self.state.last_action = ACTION_FORWARD
            return ACTION_FORWARD

    def execute(self, percept):

        ###########################
        # DO NOT MODIFY THIS CODE #
        ###########################

        bump = percept.attributes["bump"]
        dirt = percept.attributes["dirt"]
        home = percept.attributes["home"]

        # Move agent to a randomly chosen initial position
        if self.initial_random_actions > 0:
            self.log("Moving to random start position ({} steps left)".format(
                self.initial_random_actions))
            return self.move_to_random_start_position(bump)

        # Finalize randomization by properly updating position
        #  (without subsequently changing it)
        elif self.initial_random_actions == 0:
            self.initial_random_actions -= 1
            self.state.update_position(bump)
            self.state.last_action = ACTION_SUCK
            self.log("Processing percepts after position randomization")
            return ACTION_SUCK

        ########################
        # START MODIFYING HERE #
        ########################

        # Max iterations for the agent
        if self.iteration_counter < 1:
            if self.iteration_counter == 0:
                self.iteration_counter -= 1
                self.log("Iteration counter is now 0. Halting!")
                self.log("Performance: {}".format(self.performance))
            return ACTION_NOP

        self.log("Position: ({}, {})\t\tDirection: {}".
                 format(self.state.pos_x, self.state.pos_y,
                        direction_to_string(self.state.direction)))

        self.iteration_counter -= 1

        # Track position of agent
        self.state.update_position(bump)

        if bump:
            # Get an xy-offset pair based on where the agent is facing
            offset = [(0, -1), (1, 0), (0, 1), (-1, 0)][self.state.direction]

            # Mark the tile at the offset from the agent as a wall
            self.state.update_world(self.state.pos_x + offset[0], self.state.pos_y + offset[1], AGENT_STATE_WALL)

        # Update perceived state of current tile
        if dirt:
            self.state.update_world(self.state.pos_x, self.state.pos_y, AGENT_STATE_DIRT)
        else:
            self.state.update_world(self.state.pos_x, self.state.pos_y, AGENT_STATE_CLEAR)

        # Debug
        self.state.print_world_debug()

        ############################
        ### CODE ADDITIONS BELOW ###
        ############################

        ############################
        ### HELPER FXNS FOR DFS ###
        ############################

        # Check if a tile has been visited
        def is_tile_visited(tile):
            if tile is AGENT_STATE_UNKNOWN or tile is AGENT_STATE_HOME:
                return False
            else:
                return True

        # Check if the tile in front of the agent has been visited
        def front_tile_visited():
            if self.state.direction == AGENT_DIRECTION_EAST:
                return is_tile_visited(self.state.world[self.state.pos_x + 1][self.state.pos_y])

            elif self.state.direction == AGENT_DIRECTION_SOUTH:
                return is_tile_visited(self.state.world[self.state.pos_x][self.state.pos_y + 1])

            elif self.state.direction == AGENT_DIRECTION_WEST:
                return is_tile_visited(self.state.world[self.state.pos_x - 1][self.state.pos_y])

            elif self.state.direction == AGENT_DIRECTION_NORTH:
                return is_tile_visited(self.state.world[self.state.pos_x][self.state.pos_y - 1])

            return False

        # Check if tile to the right of the agent has been visited
        def right_tile_visited():
            if self.state.direction == AGENT_DIRECTION_EAST:
                return is_tile_visited(
                    self.state.world[self.state.pos_x][self.state.pos_y + 1])
            elif self.state.direction == AGENT_DIRECTION_SOUTH:
                return is_tile_visited(
                    self.state.world[self.state.pos_x - 1][self.state.pos_y])
            elif self.state.direction == AGENT_DIRECTION_WEST:
                return is_tile_visited(
                    self.state.world[self.state.pos_x][self.state.pos_y - 1])
            elif self.state.direction == AGENT_DIRECTION_NORTH:
                return is_tile_visited(
                    self.state.world[self.state.pos_x + 1][self.state.pos_y])
            return False

        # Check if the tile to the left of the agent has been visited
        def left_tile_visited():
            if self.state.direction == AGENT_DIRECTION_EAST:
                return is_tile_visited(
                    self.state.world[self.state.pos_x][self.state.pos_y - 1])
            elif self.state.direction == AGENT_DIRECTION_SOUTH:
                return is_tile_visited(
                    self.state.world[self.state.pos_x + 1][self.state.pos_y])
            elif self.state.direction == AGENT_DIRECTION_WEST:
                return is_tile_visited(
                    self.state.world[self.state.pos_x][self.state.pos_y + 1])
            elif self.state.direction == AGENT_DIRECTION_NORTH:
                return is_tile_visited(
                    self.state.world[self.state.pos_x - 1][self.state.pos_y])
            return False

        # Make the agent move forward from his direction
        def move_forward():
            self.state.last_action = ACTION_FORWARD
            return ACTION_FORWARD

        # Make the agent turn right from his direction
        def turn_right():
            self.state.direction = (self.state.direction + 1) % 4
            self.state.last_action = ACTION_TURN_RIGHT
            return ACTION_TURN_RIGHT

        # Make the agent turn right from his direction
        def turn_left():
            self.state.direction = (self.state.direction + 3) % 4
            self.state.last_action = ACTION_TURN_LEFT
            return ACTION_TURN_LEFT
        
        # Checks whether the agent is at home
        def is_home():
            return self.state.pos_x == 1 and self.state.pos_y == 1
        
        # Get the opposite direction of a direction
        def get_opposite_direction(direction):
            if direction == AGENT_DIRECTION_NORTH:
                return AGENT_DIRECTION_SOUTH
            
            if direction == AGENT_DIRECTION_EAST:
                return AGENT_DIRECTION_WEST
            
            if direction == AGENT_DIRECTION_SOUTH:
                return AGENT_DIRECTION_NORTH
            
            if direction == AGENT_DIRECTION_WEST:
                return AGENT_DIRECTION_EAST

        # Agent has traversed through every tile (DFS was completed) and agent back home
        # -- halt the program --
        def finish_cleaning():
            self.log("The agent finished cleaning all tiles and is back home!")
            self.iteration_counter = 0 # force the program to stop iterating
            self.state.last_action = ACTION_NOP
            return ACTION_NOP

        ############################
        ### DECIDE ACTION ###
        ############################        
        if dirt:
            self.log("DIRT -> choosing SUCK action!")
            self.state.last_action = ACTION_SUCK
            return ACTION_SUCK

        else:
            if bump:
                # agent couldn't move forward due to obstacle, don't save that direction
                if len(self.state.direction_stack) > 0:
                    self.state.direction_stack.pop()
                if len(self.state.direction_home_stack) > 0:
                    self.state.direction_home_stack.pop()

            # If home discovered for first time, want to start tracing directions from home
            if not self.state.home_found:
                if is_home():
                    self.state.home_found = True
            
            # If forward tile not visited, go to it
            if front_tile_visited() is False:
                # Add direction to direction stack
                self.state.direction_stack.append(self.state.direction)
                # add to home directions stack only if home has been discovered
                if self.state.home_found:
                    self.state.direction_home_stack.append(self.state.direction)

                return move_forward()

            # If left tile not visited, turn to it
            if left_tile_visited() is False:
                return turn_left()

            # If right tile not visited, turn to it
            if right_tile_visited() is False:
                return turn_right()

            # Forward/left/right have been visited, move back
                # Keep turning until we are facing the opposite direction (to move backwards)
            if len(self.state.direction_stack) > 0:
                last_direction = self.state.direction_stack[-1]
                opposite_direction = get_opposite_direction(last_direction)

                if self.state.direction == opposite_direction:
                    # Move forward to previous tile (moving backwards)
                    self.state.direction_stack.pop()
                    return move_forward()
                
                else:
                    return turn_right()
            
            # If directions stack is empty, DFS is complete -- all tiles traversed
                # Go back home
            if len(self.state.direction_home_stack) > 0:
                last_direction = self.state.direction_home_stack[-1]
                opposite_direction = get_opposite_direction(last_direction)

                if self.state.direction == opposite_direction:
                    self.state.direction_home_stack.pop()
                    return move_forward()
                
                else:
                    return turn_right()

            # If home direction stack is empty, agent is home, cleaning is done
            if is_home() and len(self.state.direction_home_stack) < 1:
                return finish_cleaning()
            
            # Catch all -- end program
            else:
                self.iteration_counter = 0
                self.state.last_action = ACTION_NOP
                return ACTION_NOP