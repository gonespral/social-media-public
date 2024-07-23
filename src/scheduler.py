"""
Scheduler class definition.
"""

import logging
import yaml
import importlib

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.triggers.cron import CronTrigger

import content
import generators
from modules import sqlite_db


def _load_config() -> dict:
    """
    Load config.yaml
    :return:
    """
    with open("config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


def _load_function(func_path: str or None) -> callable or None:
    """
    Load function from path.
    """
    if not func_path:
        return None

    module_path, func_name = func_path.rsplit(".", 1)
    # Check if module path includes a class by checking for camel case
    if any(x.isupper() for x in module_path):
        module_path, class_name = module_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        return getattr(cls, func_name)
    else:
        module = importlib.import_module(module_path)
        return getattr(module, func_name)


def _assemble_content_objects() -> list[content.ContentObject]:
    """
    Assemble content objects from config.yaml
    :return: List of content objects
    """
    content_objects = []
    for content_object_params in _load_config()["scheduler"]["content_object_params"]:
        co = content.TwitterContentObject(
            gen_func=_load_function(content_object_params["gen_func"]),
            post_func=_load_function(content_object_params["post_func"]),
            auth_func=_load_function(content_object_params["auth_func"]),
            cron=content_object_params["cron"],
            is_authorized=content_object_params["is_authorized"],
            keys_path=content_object_params["keys_path"],
        )
        content_objects.append(co)

    return content_objects


def _gen_and_auth_content_object(co: content.ContentObject) -> content.ContentObject or None:
    """
    Generate and authorize content object.
    """
    co.run_gen_func()

    # 3 attempts to authorize
    for i in range(5):
        if co.run_auth_func():
            return co
        else:
            co.run_gen_func()
    return None


class Scheduler(BlockingScheduler):
    """
    Scheduler class definition. Jobs are stored in memory.

     Core jobs:
        - _update_database : update content database from config.yaml (generate content if missing)
        - _update_scheduler : update scheduler jobs from content database

    Custom jobs:
        - Are added to scheduler with the core job _update_scheduler. Triggered at specified times.

    """

    def __init__(self):
        super().__init__()
        self.config = None
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing scheduler...")

        self.add_jobstore(MemoryJobStore(), "default")
        self.config = _load_config()
        self.load_core_jobs()

        # Run core jobs at startup
        self._update_database()
        self._update_scheduler()

    def _update_database(self):
        """
        Core job 1
        Updates the content database by assembling content objects defined in config.yaml. Content objects are
        generated and authorized if missing from database. Content objects are stored in database with their unique hash
        as primary key. Content objects are updated if hash is already found in database.
        """
        # Load content objects from config.yaml
        content_objects = _assemble_content_objects()

        # Load database
        db = sqlite_db.Database(db_file_path=self.config["paths"]["sql_database"])

        # Insert content objects into database if missing (check with hash)
        for co in content_objects:
            db.create_table(table_name=co.__class__.__name__, fields=list(co.serialize().keys()))

            # Check if content object is in database
            if db.select(table_name=co.__class__.__name__,
                         fields="*",
                         where=f"hash='{co.hash}'"):
                continue

            # Generate and authorize content object
            self.logger.info(f"Generating and authorizing {co.__class__.__name__}...")
            co = _gen_and_auth_content_object(co)
            if co:
                db.update(table_name=co.__class__.__name__,
                          fields=list(co.serialize().keys()),
                          values=list(co.serialize().values()),
                          where=f"hash='{co.hash}'")

        db.close()

    def _update_scheduler(self):
        """
        Core job 2
        Update scheduler from database. Content objects are loaded from database and added to scheduler memory jobstore.
        When a content object is triggered, it is removed from the scheduler and database. This will in turn trigger the
        core job _update_database, which will generate and authorize the content object once again.
        """
        # Load database
        db = sqlite_db.Database(db_file_path=self.config["paths"]["sql_database"])
        tables = db.list_tables()

        # Load content objects from database
        content_objects = []
        for table in tables:
            for x in db.select(table_name=table,
                               fields="*",
                               where=""):
                if table == "TwitterContentObject":
                    co = content.TwitterContentObject.deserialize(x)
                    content_objects.append(co)

        for co in content_objects:

            # Skip if not authorized
            if not co.is_authorized:
                continue

            def run_and_remove(self_, co_, db_file_path):
                """
                Remove job from scheduler and database after running.
                """
                db_ = sqlite_db.Database(db_file_path=db_file_path)
                self_.remove_job(co_.hash)
                db_.delete(table_name=co_.__class__.__name__,
                           where=f"hash='{co_.hash}'")
                co_.run_post_func()

            self.add_job(func=run_and_remove,
                         trigger=CronTrigger.from_crontab(co.cron),
                         args=[self, co, self.config["paths"]["sql_database"]],
                         name=co.__class__.__name__,
                         id=co.hash,
                         replace_existing=True)

        db.close()

    def load_core_jobs(self):
        """
        Load scheduler core jobs.
        """
        self.add_job(self._update_database, "cron", hour="*", minute="*/10", second="0")
        self.add_job(self._update_scheduler, "cron", hour="*", minute="*/10", second="0")
