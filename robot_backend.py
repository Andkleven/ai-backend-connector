from absl import app
from absl import logging
from absl import flags


flags.DEFINE_string(
    "mode",
    "prod",
    "Specify operation mode. Either: 'test' or 'prod'",
    short_name="m")

flags.DEFINE_string(
    "params_file",
    "params.yaml",
    "Specify the path to params.yaml file",
    short_name="p")


def main(_):
    params_file = FLAGS.params_file
    params = parse_options(params_file)


if __name__ == "__main__":
    FLAGS = flags.FLAGS
    app.run(main)
