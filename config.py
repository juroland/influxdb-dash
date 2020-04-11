import environs

env = environs.Env()
env.read_env()

DATABASE = env.str("DATABASE")
DATA_DURATION = env.int("DATA_DURATION", 600)  # [s]
DEBUG = env.bool("DEBUG", False)
INDICATOR = env.str("INDICATOR")
MEASUREMENT = env.str("MEASUREMENT")
REFRESH_DELAY = env.int("REFRESH_DELAY", 5)  # [s]
TAG = env.str("TAG")

EXTERNAL_STYLESHEETS = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
