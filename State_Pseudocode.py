class State:
    def __init__(self, center, identifier):
        """Initializes a state object with the center as a latitude/longitude
        tuple and a unique integer identifier."""

    def probability_to(self, destination_id):
        """Returns probability for this state to `destination_id`."""

    def expected_fare_to(self, destination_id):
        """Returns expected fare to go from this state to `destination_id`."""

    def expected_duration_to(self, destination_id):
        """Returns expected duration to go from this state to `destination_id`."""

    def add_destination(self, destination_id, fare, duration):
        """Adds this `destination_id` as a destination state from this state 
        based on a single ride."""

    def update_center(self):
        """Helper method for k-means. Returns difference between new center 
        and old center as tuple."""
        latitude, longitude = self.center
        distance_difference = ((new_latitude - latitude) ** 2 + \
                               (new_longitude - longitude) ** 2) ** 1 / 2
        return distance_difference

    def distance_from_center(self, location):
        """Helper method for k-means."""
        latitude, longitude = location
        center_latitude, center_longitude = self.center
        return ((center_latitude - latitude) ** 2 + \
               (center_longitude - longitude) ** 2)

    @property
    def sum_of_squared_errors(self):
        """Helper method for k-means."""
        total_distance = 0
        for data_point in self.stored_data:
            location = data_point
            total_distance += self.distance_from_center(location)
        return total_distance

    def next_state(self):
        """Returns a random destination state based on the Markov probabilities
        along with the expected cost of a ride there and the expected duration
        of the ride there."""
        return next_state_to_go_to


