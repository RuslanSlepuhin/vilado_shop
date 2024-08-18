import configparser
from variables import variables

config = configparser.ConfigParser()
config.read(variables.config_path)