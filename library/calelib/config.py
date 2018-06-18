import configparser
import os


class Config:
    def __init__(self):
        """
        Class for work with config file
        :param path: path of config file
        """
        self.path = 'config.ini'
        self.section = 'Settings'
        if not os.path.exists(self.path):
            self.__create_config()

    def __create_config(self):
        """
        Creates config file with default settings
        """
        config = configparser.ConfigParser()
        config.add_section(self.section)
        config.set(self.section, 'logging_path', 'tmp/logging.log')
        config.set(self.section, 'logging_level', 'INFO')
        config.set(self.section, 'logging_format', '%%(asctime)s %%(levelname)s %%(message)s')
        if not os.path.exists('tmp'):
            os.mkdir('tmp')
        with open(self.path, 'w') as config_file:
            config.write(config_file)

    def get_field(self, key):
        """
        Access to the fields of config
        :param key: name of the field what value should be returned
        :return: value from field with name 'key'
        """
        config = configparser.ConfigParser()
        config.read(self.path)
        value = config.get(self.section, key)
        return value

    def add_field(self, field):
        config = configparser.ConfigParser()
        config.read(self.path)
        config.set(self.section, field, '')
        with open(self.path, 'w') as config_file:
            config.write(config_file)

    def set_field(self, field, field_value):
        config = configparser.ConfigParser()
        config.read(self.path)
        config.set(self.section, field, field_value)
        with open(self.path, 'w') as config_file:
            config.write(config_file)
