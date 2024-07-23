"""
Content Object definitions.
"""

import ast
import json
from dataclasses import dataclass
from copy import deepcopy
import pickle
from hashlib import sha256
import inspect

import croniter


def _convert_value_types(attr_dict: dict) -> dict:
    """
    Convert values to correct types
    :param attr_dict: Dict of ContentObject
    :return: Dict of ContentObject
    """
    for k, v in attr_dict.items():
        if v == "None":
            attr_dict[k] = None
        elif v == "True":
            attr_dict[k] = True
        elif v == "False":
            attr_dict[k] = False
        elif v.isdigit():
            attr_dict[k] = int(v)
        elif v.replace(".", "", 1).isdigit():
            attr_dict[k] = float(v)
        # Check if object is a dict or list
        elif v.startswith("{") and v.endswith("}"):
            attr_dict[k] = ast.literal_eval(v)
            attr_dict[k] = _convert_value_types(attr_dict[k])
        elif v.startswith("[") and v.endswith("]"):
            attr_dict[k] = ast.literal_eval(v)
            attr_dict[k] = _convert_value_types(attr_dict[k])
        else:
            attr_dict[k] = v
    return attr_dict


# ContentObject base class definition.
@dataclass
class ContentObject:
    """
    ContentObject base class.
    :param gen_func: Callable that returns a dict of attributes to update.
    :param post_func: Callable that returns a dict of attributes to update.
    :param cron: Cron expression to run gen_func and post_func. If None, run immediately.
    :param auth_func: Callable that returns True if the ContentObject is authorized to post.
    """
    gen_func: callable
    post_func: callable
    auth_func: callable = None
    cron: str = None
    is_authorized: bool = False
    keys_path: str = None

    def __post_init__(self):
        # Hash attributes to create unique identifier. This does not depend on subclass annotations.
        gen_func_str = inspect.getsource(self.gen_func)
        post_func_str = inspect.getsource(self.post_func)
        auth_func_str = inspect.getsource(self.auth_func)
        self.hash = sha256((gen_func_str + post_func_str + auth_func_str + self.cron).encode()).hexdigest()

        # Validate cron expression
        if self.cron:
            try:
                croniter.croniter(self.cron)
            except Exception as e:
                raise ValueError(f"Invalid cron expression: {self.cron}")

        # Load keys
        if self.keys_path:
            with open(self.keys_path, "r") as f:
                self.keys = json.load(f)
        else:
            self.keys = {}

    def run_gen_func(self):
        """
        Run gen_func and update attributes. Generation function must return a dict with keys matching
        the attributes of the ContentObject. Arguments to gen_func must be the "keys" dict.
        """
        res = self.gen_func(self.keys)

        if not isinstance(res, dict):
            raise ValueError(f"gen_func must return a dict. Received: {res}")

        required_keys = self.__annotations__.keys()
        if not all([k in required_keys for k in res.keys()]):
            raise ValueError(f"gen_func must return all required keys: {required_keys}")

        unrecognized_keys = [k for k in res.keys() if k not in required_keys]
        if unrecognized_keys:
            raise ValueError(f"gen_func returned unrecognized keys: {unrecognized_keys}")

        for k, v in res.items():
            setattr(self, k, v)

    def run_post_func(self):
        """
        Run post_func and update attributes. Arguments to post_func must be the ContentObject dict of attributes, and
        the "keys" dict.
        """
        if self.is_authorized:
            content_dict = {}
            for annotation in self.__annotations__.keys():
                content_dict[annotation] = getattr(self, annotation)
            return self.post_func(content_dict=content_dict,
                                  keys=self.keys)
        else:
            raise ValueError("ContentObject is not authorized to run post.")

    def run_auth_func(self):
        """
        Run auth_func and update attributes. Arguments to auth_func must be the ContentObject dict of attributes, and
        the "keys" dict.
        """
        # Names of funcs, not funcs themselves
        content_dict = {
            "gen_func": self.gen_func.__name__,
            "post_func": self.post_func.__name__,
            "auth_func": self.auth_func.__name__,
            "cron": self.cron,
            "keys_path": self.keys_path,
        }
        for annotation in self.__annotations__.keys():
            content_dict[annotation] = getattr(self, annotation)

        if not self.is_authorized and self.auth_func:
            if self.auth_func(content_dict=content_dict,
                              keys=self.keys):
                self.is_authorized = True
                return True
            else:
                self.is_authorized = False
                return False
        else:
            return True

    def serialize(self) -> dict:
        """
        Serialize ContentObject
        :return: Dict of ContentObject
        """
        # Deep copy object
        obj = deepcopy(self)
        obj.gen_func = pickle.dumps(obj.gen_func).hex()
        obj.post_func = pickle.dumps(obj.post_func).hex()
        obj.auth_func = pickle.dumps(obj.auth_func).hex()
        attr_dict = obj.__dict__

        # Convert all to strings
        for k, v in attr_dict.items():
            attr_dict[k] = str(v)

        return attr_dict

    @classmethod
    def deserialize(cls, attr_dict: dict):
        """
        Deserialize ContentObject (or inherited class) from pickle bytes object.
        :param attr_dict: Dict of ContentObject
        :return: ContentObjects
        """
        # Convert values to correct types
        attr_dict = _convert_value_types(attr_dict)

        obj = cls.__new__(cls)
        obj.__dict__.update(attr_dict)
        obj.gen_func = pickle.loads(bytes.fromhex(obj.gen_func))
        obj.post_func = pickle.loads(bytes.fromhex(obj.post_func))
        obj.auth_func = pickle.loads(bytes.fromhex(obj.auth_func))

        return obj


# TwitterContentObject class definition.
@dataclass
class TwitterContentObject(ContentObject):
    """
    TwitterContentObject class.
    :param text: Tweet text.
    :param thread: Tweet thread. Optional.
    :param media: Path to media file. Optional.
    :param in_reply_to_tweet_id: Tweet id to reply to. Optional.
    """
    text: str = None
    thread: str = None
    media: str = None
    in_reply_to_tweet_id: str = None
