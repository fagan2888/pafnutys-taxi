import random

class State:
    def __init__(self, center, identifier):
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
        self.center = center
        self.id = identifier
        self.transition_counts = dict() # key: destination id, value: total number of rides there
        self.total_fare = dict() # key: destination id, value: total fare for all rides there
        self.total_duration = dict() # key: destination id, value: total duration for all rides there
        self.stored_data = set()

        # for k-means
        self.total_latitude = 0
        self.total_longitude = 0
        self.number_of_positions = 0

    def probability_to(self, destination_id):
        if destination_id not in self.transition_counts:
            return 0
        total = sum(self.transition_counts.values())
        destination_count = self.transition_counts[destination_id]
        return destination_count / total

    def expected_fare_to(self, destination_id):
        if destination_id not in self.total_fare:
            return 0
        total_fare_to_destination = self.total_fare[destination_id]
        destination_count = self.transition_counts[destination_id]
        return total_fare_to_destination / destination_count

    def expected_duration_to(self, destination_id):
        if destination_id not in self.total_duration:
            return 0
        total_duration_to_destination = self.total_duration[destination_id]
        destination_count = self.transition_counts[destination_id]
        return total_duration_to_destination / destination_count

    def add_destination(self, destination_id, fare, duration):
        if destination_id not in self.transition_counts:
            self.transition_counts[destination_id] = 0
            self.total_fare[destination_id] = 0
            self.total_duration[destination_id] = 0
        self.transition_counts[destination_id] += 1
        self.total_fare[destination_id] += fare
        self.total_duration[destination_id] += duration

    def add_position(self, position):
        latitude, longitude = position
        self.total_latitude += latitude
        self.total_longitude += longitude
        self.number_of_positions += 1

    def store_data(self, data_point):
        self.stored_data.add(data_point)

    def clear_stored_data(self):
        self.stored_data = set()

    def get_all_points(self):
        return self.stored_data

    def update_center(self):
        """Returns difference between new center and old center as tuple."""
        new_latitude = self.total_latitude / self.number_of_positions
        new_longitude = self.total_longitude / self.number_of_positions
        latitude, longitude = self.center
        distance_difference = ((new_latitude - latitude) ** 2 + \
                               (new_longitude - longitude) ** 2) ** 1 / 2
        self.center = (new_latitude, new_longitude)

        self.total_latitude = 0
        self.total_longitude = 0
        self.number_of_positions = 0
        return distance_difference

    def distance_from_center(self, location):
        latitude, longitude = location
        center_latitude, center_longitude = self.center
        return ((center_latitude - latitude) ** 2 + \
               (center_longitude - longitude) ** 2) # ** (1 / 2)

    @property
    def sum_of_squared_errors(self):
        total_distance = 0
        for data_point in self.stored_data:
            location = data_point
            total_distance += self.distance_from_center(location)
        return total_distance

    def next_state(self):
        """Returns a random destination state based on the Markov probabilities
        along with the expected cost of a ride there and the expected duration
        of the ride there."""
        cumulative_probability = 0
        cumulative_probability_list = []
        transition_states = self.transition_counts.keys()
        for destination_id in transition_states:
            cumulative_probability += self.probability_to(destination_id)
            cumulative_probability_list.append(cumulative_probability)
        assert abs(cumulative_probability - 1) <= 1e-3, "{}".format(cumulative_probability)

        random_number = random.random()
        counter = 0
        while counter <= len(transition_states):
            if random_number <= cumulative_probability_list[counter]:
                destination_id = transition_states[counter]
                expected_fare = expected_fare_to(destination_id)
                expected_duration = expected_duration_to(destination_id)
                return destination_id, expected_fare, expected_duration
            counter += 1

        raise ValueError("Could not find a valid next_state")

