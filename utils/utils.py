from ruamel.yaml import YAML


def parse_options(path_to_options_file):
    with open(path_to_options_file, 'r') as f:
        yaml = YAML()
        options = yaml.load(f)
    return options
