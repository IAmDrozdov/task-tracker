import configparser
import os


class Config:
    """Represents Config instance"""

    def __init__(self):
        self.path = 'config.ini'
        self.section = 'Settings'
        if not os.path.exists(self.path):
            self.__create_config()

    def __create_config(self):
        """Creates config file with default settings"""
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
        Return value of field
        Args:
            key(string): name of the field what value should be returned
        """
        config = configparser.ConfigParser()
        config.read(self.path)
        value = config.get(self.section, key)
        return value

    def add_field(self, field):
        """
        Add new field to config
        Args:
            field(str): name of field
        """
        config = configparser.ConfigParser()
        config.read(self.path)
        config.set(self.section, field, '')
        with open(self.path, 'w') as config_file:
            config.write(config_file)

    def set_field(self, field, field_value):
        """
        Set value of field
        Args:
            field(str):  name of the field what value should be set
            field_value(str): value what will be putted to the field
        """
        config = configparser.ConfigParser()
        config.read(self.path)
        config.set(self.section, field, field_value)
        with open(self.path, 'w') as config_file:
            config.write(config_file)
