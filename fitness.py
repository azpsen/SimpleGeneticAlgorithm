

class FitnessFunc:
    # Base class, if used as-is will give no reward value for the given action
    # Constructor can be used to build a custom fitness function
    def __init__(
            self,
            wall_hit_reward=0,
            move_to_can_reward=0,
            pick_up_can_reward=0,
            fail_pickup_reward=0,
    ):
        self.wall_hit_reward = wall_hit_reward
        self.move_to_can_reward = move_to_can_reward
        self.pick_up_can_reward = pick_up_can_reward
        self.fail_pickup_reward = fail_pickup_reward

    def __call__(self, world, action):
        # Return the reward value of an action

        # Decode percept into the values of each cell around Robby
        percept = world.getPercept()
        n = percept[0]
        s = percept[1]
        e = percept[2]
        w = percept[3]
        h = percept[4]

        # Decide value of each action

        # Robby runs into a wall
        if action == "MoveNorth" and world.robbyRow == world.topRow or \
                action == "MoveSouth" and world.robbyRow == world.bottomRow or \
                action == "MoveEast" and world.robbyCol == world.rightCol or \
                action == "MoveWest" and world.robbyCol == world.leftCol:
            return self.wall_hit_reward

        # Robby moves into a cell containing a can
        if action == "MoveNorth" and n == "C" or \
                action == "MoveSouth" and s == "C" or \
                action == "MoveEast" and e == "C" or \
                action == "MoveWest" and w == "C":
            return self.move_to_can_reward

        # Robby picks up a can
        if action == "PickUpCan" and h == "C":
            return self.pick_up_can_reward

        # Robby tries to pick up a can in an empty cell
        if action == "PickUpCan" and h == "E":
            return self.fail_pickup_reward

        return 0


class RewardCanCollecting(FitnessFunc):
    # Only reward collecting cans, all other actions have no reward
    def __init__(self):
        super().__init__()
        self.pick_up_can_reward = 1


class PunishWallHits(FitnessFunc):
    # Reward can collection and punish wall hits
    def __init__(self):
        super().__init__()
        self.pick_up_can_reward = 2
        self.wall_hit_reward = -1
