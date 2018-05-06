import configparser
import os


class Config:
    def __init__(self, path):
        """
        Class for work with config file
        :param path: path of config file
        """
        self.path = path
        self.section = 'Settings'
        if not os.path.exists(self.path):
            self.create_config()

    def create_config(self):
        """
        Creates config file with default settings
        """
        config = configparser.ConfigParser()
        config.add_section(self.section)
        config.set(self.section, 'database', 'database.json')
        config.set(self.section, 'pid', 'pid.ini')
        config.set(self.section, 'status_finished', 'finished')
        config.set(self.section, 'status_unfinished', 'unfinished')
        config.set(self.section, 'logger_output', 'logging.log')

        with open(self.path, 'w') as config_file:
            config.write(config_file)

    def get_config_field(self, key):
        """
        Access to the fields of config
        :param key: name of the field what value should be returned
        :return: value from field with name 'key'
        """
        config = configparser.ConfigParser()
        config.read(self.path)
        value = config.get(self.section, key)
        return value
