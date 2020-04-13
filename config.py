import environs

env = environs.Env()
env.read_env()

DATABASE = env.str("DATABASE")
DEBUG = env.bool("DEBUG", False)
INDICATOR = env.str("INDICATOR")
MEASUREMENT = env.str("MEASUREMENT")
TAG = env.str("TAG")

EXTERNAL_STYLESHEETS = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
