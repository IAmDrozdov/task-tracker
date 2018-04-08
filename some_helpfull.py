def print_cont(contain):
    """
    recursively do something with all elements in container
    :param contain: container with tasks
    :return: print all tasks with their subtasks and etc.
    в следующий раз попробовать передавать параметром функцию, хоторую надо делать с каждым элементом,
    в таком случае можно будет реализовать более ёмко "поиск", "принт", и всякое такое!!!!!!!
    """

    if contain:
        for task in contain:
            print(task)
            print_cont(task['subtasks'])
