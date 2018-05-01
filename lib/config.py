import configparser
import os


class Config:
    def __init__(self, path):
        self.path = path
        self.section = 'Settings'
        if not os.path.exists(self.path):
            self.create_config()

    def create_config(self):
        config = configparser.ConfigParser()
        config.add_section(self.section)
        config.set(self.section, 'database', 'database.json')
        config.set(self.section, 'delimiter', '_')
        config.set(self.section, 'pid', 'pid.ini')
        config.set(self.section, 'status_finished', 'finished')
        config.set(self.section, 'status_unfinished', 'unfinished')

        with open(self.path, 'w') as config_file:
            config.write(config_file)

    def get_config_field(self, key):
        config = configparser.ConfigParser()
        config.read(self.path)
        value = config.get(self.section, key)
        return value
