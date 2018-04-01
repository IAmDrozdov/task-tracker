class Randomizer:
    @staticmethod
    def get_actual_index(container):
        """
        this method calculate pseudorandom number
        :param container: should be only list
        :return: int number what calculating incrementing 'id' of last
        item in container
        """
        if len(container) == 0:
            return 1
        else:
            return container[len(container) - 1]['id'] + 1
