"""
Entry point. Initializes scheduler and starts the program.
"""

import logging
import yaml

import scheduler

with open("config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# Configure logger
logfile = config["paths"]["main_logfile"]
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(levelname)s : %(asctime)s : %(name)s : %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.info("Starting...")

# Print logging info to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(levelname)s : %(asctime)s : %(name)s : %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

if __name__ == "__main__":
    scheduler = scheduler.Scheduler()
    scheduler.start()
