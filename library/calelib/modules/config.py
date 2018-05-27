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
            self.__create_config()

    def __create_config(self):
        """
        Creates config file with default settings
        """
        config = configparser.ConfigParser()
        config.add_section(self.section)
        config.set(self.section, 'database_path', 'tmp/database.json')
        config.set(self.section, 'pid_path', 'tmp/pid.ini')
        config.set(self.section, 'logging_path', 'tmp/logging.log')
        config.set(self.section, 'logging_level', 'INFO')
        config.set(self.section, 'logging_format', '%%(asctime)s %%(levelname)s %%(message)s')
        if not os.path.exists('tmp'):
            os.mkdir('tmp')
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
