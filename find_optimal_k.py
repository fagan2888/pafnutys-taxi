def find_optimal_k(raw, k_list):
    y = []
    x = []
    k_dict = {}
    for t in trials:
        for k in k_list:
            if k not in k_dict:
                k_dict[k] = []
            try:
                m = MarkovChain(raw[:1000], k)
                x.append(k)
                y.append(m.sum_of_square_error())
            except ZeroDivisionError:
                print("hello")
    return x, y
