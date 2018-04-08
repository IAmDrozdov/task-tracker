def get_actual_index(container, is_sub=True):
    """
    this method calculate pseudorandom number
    :param container: should be only list
           is_sub: indicator for what we return index
    :return: int number what calculating incrementing 'id' of last
    item in container
    """
    if is_sub:
        if len(container) == 0:
            return '1'
        else:
            pre_id = container[len(container) - 1]['id'].split('_')
            return str(int(pre_id[len(pre_id) - 1]) + 1)
    else:
        return str(int(container[len(container) - 1].id) + 1) if len(container) != 0 else '1'

