import json
import re
import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme

PARSER_SIGNALS_FAILURE = 418  # Universal Teapot error code


class BaseParser:
    # Add definitions here for how we want the logging for the parsers to be processed. 
    # Make these class wide. This goes along with an update to requirements in stockpile for 
    # better logging. 
    format = "%(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    console = Console(theme=Theme({"logging.level.warning": "yellow"}),width=240)
    level=logging.DEBUG
    logging.basicConfig(
        level=level,
        format=format,
        datefmt=datefmt,
        handlers=[RichHandler(rich_tracebacks=True, markup=True, console=console,show_time=False)]
    )

    for logger_name in logging.root.manager.loggerDict.keys():
        if logger_name in ("aiohttp.server", "asyncio"):
            continue
        else:
            logging.getLogger(logger_name).setLevel(100)
    logging.getLogger("markdown_it").setLevel(logging.WARNING)
    logging.captureWarnings(True)


    def __init__(self, parser_info):
        self.mappers = parser_info['mappers']
        self.used_facts = parser_info['used_facts']
        self.source_facts = parser_info['source_facts']

    @staticmethod
    def set_value(search, match, used_facts):
        """
        Determine the value of a source/target for a Relationship
        :param search: a fact property to look for; either a source or target fact
        :param match: a parsing match
        :param used_facts: a list of facts that were used in a command
        :return: either None, the value of a matched used_fact, or the parsing match
        """
        if not search:
            return None
        for uf in used_facts:
            if search == uf.trait:
                return uf.value
        return match

    @staticmethod
    def email(blob):
        """
        Parse out email addresses
        :param blob:
        :return:
        """
        return re.findall(r'[\w\.-]+@[\w\.-]+', blob)

    @staticmethod
    def filename(blob):
        """
        Parse out filenames
        :param blob:
        :return:
        """
        return re.findall(r'\b\w+\.\w+', blob)

    @staticmethod
    def line(blob):
        """
        Split a blob by line
        :param blob:
        :return:
        """
        return [x.rstrip('\r') for x in blob.split('\n') if x]

    @staticmethod
    def ip(blob):
        return re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', blob)

    @staticmethod
    def broadcastip(blob):
        return re.findall(r'(?<=broadcast ).*', blob)

    @staticmethod
    def load_json(blob):
        try:
            return json.loads(blob)
        except Exception:
            return None
