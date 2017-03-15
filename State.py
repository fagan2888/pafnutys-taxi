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
        self.transition_counts = dict()
        self.stored_data = set()

        # for k-means
        self.total_latitude = 0
        self.total_longitude = 0
        self.number_of_positions = 0

    def probability_to(self, destination_id):
        total = sum(self.transition_counts.values())
        if destination_id not in self.transition_counts:
            return 0
        destination_count = self.transition_counts[destination_id]
        return destination_count / total

    def add_destination(self, destination_id):
        if destination_id not in self.transition_counts:
            self.transition_counts[destination_id] = 0
        self.transition_counts[destination_id] += 1

    def add_position(self, position):
        latitude, longitude = position
        self.total_latitude += latitude
        self.total_longitude += longitude
        self.number_of_positions += 1

    def store_data(self, data_point):
        """if data_point is a start point then it will contain fare and 
        duration of the ride also passed in inside the tuple"""
        self.stored_data.add(data_point)

    def clear_stored_data(self):
        self.stored_data = set()

    def is_start(self, data_point):
        return len(data_point) == 3

    @property
    def average_cost(self):
        total_fare = 0
        total_number_of_start_points = 0
        for data_point in self.stored_data:
            if is_start(data_point):
                total_number_of_start_points += 1
                position, fare, time = data_point
                total_fare += fare
        return total_fare_so_far / total_number_of_start_points

    def update_center(self):
        """Returns difference between new center and old center as tuple."""
        new_latitude = self.total_latitude / self.number_of_positions
        new_longitude = self.total_longitude / self.number_of_positions
        latitude, longitude = self.center
        difference = (abs(new_latitude - latitude), abs(new_longitude - longitude))
        self.center = (new_latitude, new_longitude)

        self.total_latitude = 0
        self.total_longitude = 0
        self.number_of_positions = 0
        return difference

