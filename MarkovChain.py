import State as State
importlib.reload(State)

class MarkovChain:
    # num centers are we picking for k-means
    def __init__(self, raw, k, epsilon = 1e-12):
        self.state_set = set()
        self.id_to_state = {}
        self.adj_matrix = None
        self.raw = raw
        self.k = k

        self.initialize_centers(k)

        self.build_states_kmeans(1000, epsilon)

        self.add_points_edges()
        self.make_adjacency_matrix()

    def initialize_centers(self, k):
        ind = [i for i in range(len(self.raw))]
#         rand.shuffle(ind)
        centers = ind[:k]
        # initialize centers
        ident = 0
        for c_ind in centers:
            # out of convenience, we aren't messing with pickup lat lon
            lat = self.raw.ix[c_ind]["pickup_latitude"]
            lon = self.raw.ix[c_ind]["pickup_longitude"]
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
            duration = self.row_to_trip_duration_seconds(row)
            tdistance = self.row_to_distance(row)

            #Add points to respective states
            closest_to_start.store_data(pos_start)
            closest_to_end.store_data(pos_end)

            ##Add this edge to markov state
            closest_to_start.add_destination(closest_to_end.id, fare, duration)


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


#     def random_walk_given_time_cap(self, start_id, duration_cap):
#         while

    def random_walk(self, start_id, walk_length):
        total_duration = 0
        total_fare = 0
        states_visited = []
        next_id = start_id
        for i in range(walk_length):
            states_visited.append(next_id)
            s = self.get_state(next_id)
            next_id, fare, duration = s.next_state()
            total_fare += fare
            total_duration += duration
        return states_visited, total_fare, total_duration

    def random_walk_simulator(self, num_of_simulations=100, walk_length=10):
        average_fare_by_state = []
        average_duration_by_state = []
        for state_id in range(self.k):
            list_of_random_walks = []
            for _ in range(num_of_simulations):
                random_walk_simulation = self.random_walk(state_id, walk_length)
                list_of_random_walks.append(random_walk_simulation)
            total_fare = sum([walk[1] for walk in list_of_random_walks])
            average_fare = total_fare / num_of_simulations
            average_fare_by_state.append(average_fare)
            total_duration = sum([walk[2] for walk in list_of_random_walks])
            average_duration = total_duration / num_of_simulations
            average_duration_by_state.append(average_fare)
        return average_fare_by_state, average_duration_by_state

    def traveling_salesman(self, start_id):
        total_duration = 0
        total_fare = 0
        states_visited = []
        next_id = start_id
        need_to_visit = set(self.id_to_state.keys()[:])
        need_to_visit.remove(start_id)
        while(len(need_to_visit)):
            states_visited.append(next_id)
            s = self.get_state(next_id)
            next_id, fare, duration = s.next_state()
            total_fare += fare
            total_duration += duration
            need_to_visit.remove(next_id)
        return states_visited, len(states_visited), total_fare, total_duration
    
    def traveling_salesman_simulator(self, num_of_simulations=100):
        average_number_of_states_by_state = []
        average_duration_by_state = []
        for state_id in range(self.k):
            for _ in range(num_of_simulations):
                states_visited, number_of_states_visited, fare, duration = self.traveling_salesman(state_id)
                total_number_of_states += number_of_states_visited
#                 total_fare += fare
                total_duration += duration
            average_number_of_states = total_number_of_states / num_of_simulations
            average_number_of_states_by_state.append(average_number_of_states)
            average_duration = total_duration / num_of_simulations
            average_duration_by_state.append(average_duration)
        return average_number_of_states_by_state, average_duration_by_state

    ##
    # GETTERS
    ##
    def get_invariant(self):
        adjm = self.get_adjacency_matrix()
        S, U = np.linalg.eig(adjm.T)
        inv_dist = U.T[0]
        norm_inv_dist = inv_dist / float(sum(inv_dist))
        return norm_inv_dist

    def get_state(self, iden):
        return self.id_to_state[iden]

    def get_state_set(self):
        return self.state_set

    def get_adjacency_matrix(self):
        return self.adj_matrix

    ###
    # HELPER METHODS
    ###
    def find_closest_state(self, pos):
        def distance(state, pos):
            clat, clon = state.center
            return float(((clat - pos[0])**2 + (clon - pos[1])**2))**0.5
        closest = None
        min_dist = None
        for state in self.state_set:
            d = distance(state, pos)
            if closest == None or d < min_dist:
                closest = state
                min_dist = d
        assert(closest != None)
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
    def row_to_trip_duration_seconds(self, row):
        diff = row["pickup_datetime"] - row["dropoff_datetime"]
        return diff.total_seconds()


    def transition_probability(self, i, j):
        return self.id_to_state[i].probability_to(j)
