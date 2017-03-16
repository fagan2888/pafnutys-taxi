class MarkovChain:
    # num centers are we picking for k-means
    def __init__(self, raw, k):
        self.state_set = set()
        self.id_to_state = {}
        self.adj_matrix = None
        self.raw = raw

        self.initialize_centers(k)
        epsilon = 1e-3
        self.build_states_kmeans(1001, epsilon)

        self.add_points_edges()
        self.make_adjacency_matrix()

    def initialize_centers(self, k):
        ind = [i for i in range(len(self.raw))]
        rand.shuffle(ind)
        centers = ind[:k]
        # initialize centers
        ident = 0
        for c_ind in centers:
            # out of convenience, we aren't messing with pickup lat lon
            lat = self.raw.ix[c_ind]["dropoff_latitude"]
            lon = self.raw.ix[c_ind]["dropoff_longitude"]
            s = State.State((lat, lon), ident)
            self.state_set.add(s)
            self.id_to_state[ident] = s
            ident += 1

    def build_states_kmeans(self, iterations, epsilon):
        # run kmeans algorithm
        min_diff = 1e6
        while iterations > 0 and min_diff > epsilon:
            for ind, row in self.raw.iterrows():
                pos_start, pos_end = self.row_to_positions(row)
                closest_to_start = self.find_closest_state(pos_start)
                closest_to_end = self.find_closest_state(pos_end)

                closest_to_start.add_position(pos_start)
                closest_to_end.add_position(pos_end)
            max_diff = 0
            for s in self.state_set:
                max_diff = max(max_diff, s.update_center())
            min_diff = min(min_diff, max_diff)
            iterations -= 1

    def add_points_edges(self):
        for s in self.state_set:
            s.clear_stored_data()
        for ind, row in self.raw.iterrows():
            pos_start, pos_end = self.row_to_positions(row)
            closest_to_start = self.find_closest_state(pos_start)
            closest_to_end = self.find_closest_state(pos_end)

            fare = self.row_to_fare(row)
            tdistance = self.row_to_distance(row)

            #Add points to respective states
            closest_to_start.store_data((pos_start, fare, tdistance))
            closest_to_end.store_data(((pos_end),))

            ##Add this edge to markov state
            closest_to_start.add_destination(closest_to_end.id)


    def make_adjacency_matrix(self):
        self.adj_matrix = np.ndarray(shape=(len(self.state_set), len(self.state_set)), dtype=float, order='C')
        for i in sorted(self.id_to_state.keys()):
            for j in sorted(self.id_to_state.keys()):
                self.adj_matrix[i][j] = self.transition_probability(i, j)

    def sum_of_square_error(self):
        total = 0
        for s in self.state_set:
            total += s.sum_of_squared_errors
        return total

    ##
    # GETTERS
    ##
    def get_adjacency_matrix(self):
        return self.adj_matrix

    ###
    # HELPER METHODS
    ###
    def find_closest_state(self, pos):
        def distance(state, pos):
            clat, clon = state.center
            return ((clat - pos[0])**2 + (clon - pos[1])**2)**0.5
        closest = None
        min_dist = None
        for state in self.state_set:
            d = distance(state, pos)
            if closest == None or d < min_dist:
                closest = state
                min_dist = d
        return closest

    def row_to_positions(self, row):
        lats = row["pickup_latitude"]
        lons = row["pickup_longitude"]
        pos_start = (lats, lons)

        late = row["dropoff_latitude"]
        lone = row["dropoff_longitude"]
        pos_end = (late, lone)

        return pos_start, pos_end

    def row_to_fare(self, row):
        return row["payment_amount"]
    def row_to_distance(self, row):
        return row["trip_distance"]

    def transition_probability(self, i, j):
        return self.id_to_state[i].probability_to(j)
