def print_cont(contain):
    """
    recursively do something with all elements in container
    :param contain: container with tasks
    :return: print all tasks with their subtasks and etc.
    """
    if contain:
        for task in contain:
            print(task)
            print_cont(task['subtasks'])
