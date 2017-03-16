import State as State

class MarkovChain:
    def __init__(self, raw, k, epsilon=1e-12):
        self.initialize_centers(k)
        self.build_states_kmeans(1000, epsilon)
        self.add_points_edges()
        self.make_adjacency_matrix()

    def initialize_centers(self, k):
        """Extract locations from the raw data and create states from these 
        data points."""

    def build_states_kmeans(self, iterations, epsilon):
        "Runs K-means algorithm."
        while iterations > 0 and min_diff > epsilon:
            for ind, row in self.raw.iterrows():
                pos = self.row_to_positions(row)
                closest = self.find_closest_state(pos)
                closest.add_position(pos)
            
            update_centers()
            iterations -= 1

    def add_points_edges(self):
        """Creates transition between states based on all data points."""

    def make_adjacency_matrix(self):
        """Creates adjacency matrix from transition probabilities."""

    def sum_of_square_error(self):
        """Sums up squared error total for each state."""
        total = 0
        for s in self.state_set:
            total += s.sum_of_squared_errors
        return total

    def random_walk(self, start_id, walk_length):
        """Runs a single random walk from a `start_id` for a `walk_length`."""
        total_duration, total_fare, states_visited = 0, 0, []
        next_id = start_id
        for i in range(walk_length):
            states_visited.append(next_id)
            s = self.get_state(next_id)
            next_id, fare, duration = s.next_state()
            total_fare += fare
            total_duration += duration
        return states_visited, total_fare, total_duration

    def random_walk_simulator(self, num_of_simulations=100, walk_length=10):
        """Runs `num_of_simulations` of random walks for walks of length `walk_length`
        for a walk starting in each state."""
        average_fare_by_state = []
        average_duration_by_state = []
        for state_id in range(self.k):
            list_of_random_walks = []
            for _ in range(num_of_simulations):
                random_walk_simulation = self.random_walk(state_id, walk_length)
                list_of_random_walks.append(random_walk_simulation)
        return average_fare_by_state, average_duration_by_state

    def get_invariant(self):
        """Gets invaraint distribution of the MarkovChain."""
        adjm = self.get_adjacency_matrix()
        S, U = np.linalg.eig(adjm.T)
        inv_dist = U.T[0]
        norm_inv_dist = inv_dist / float(sum(inv_dist))
        return norm_inv_dist

