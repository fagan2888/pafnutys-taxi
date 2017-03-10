number_of_states = 0

class State:
    def __init__(self, center):
        """
        `center` is a (lat, long) tuple
        `transition_counts` is the counts between this state and all other states. 
        The transition probabilities can be calcluated on demand

        >>> state0 = State((10, 15))
        >>> state1 = State((15, 20))
        >>> state0.count
        0
        >>> state0.center
        (10, 15)
        >>> state1.count
        1
        """
        global number_of_states
        self.center = center
        self.identifier = number_of_states
        number_of_states += 1
        self.transition_counts = dict()

        # for k-means
        self.total_latitude = 0
        self.total_longitude = 0
        self.number_of_positions = 0

    def probability_to(self, state):
        total = sum(self.transition_counts.values())
        destination_count = self.transition_counts[state]
        return destination_count / total

    def add_destination(self, destination):
        destination_identifier = destination.identifier
        if destination_identifier not in transition_counts:
            transition_counts[destination_identifier] = 0
        transition_counts[destination_identifier] += 1

    def add_position(self, position):
        latitude, longitude = position
        self.total_latitude += latitude
        self.total_longitude += longitude

    def update_center(self):
        new_latitude = self.total_latitude / self.number_of_positions
        new_longitude = self.total_longitude / self.number_of_positions
        self.center = (new_latitude, new_longitude)

        self.total_latitude = 0
        self.total_longitude = 0
        self.number_of_positions = 0
