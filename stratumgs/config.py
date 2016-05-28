"""
.. module stratumgs.config

Loads the configuration and provides a method for accessing it.
"""

import configparser
import os


# The default value and type of each configuration parameter
_CONFIG_VALUES = {
    "global": {
        "debug": (bool, True)
    },
    "web_server": {
        "host": (str, ""),
        "port": (int, 8888)
    },
    "client_server": {
        "host": (str, ""),
        "port": (int, 8889)
    }
}

# The configuration object itself
_CONFIG = configparser.ConfigParser()

# Look for stratumgs.conf in project root.
# If that doesn't exist, look for /etc/stratumgs.conf.
path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "stratumgs.conf"))
if os.path.exists(path):
    _CONFIG.read(path)
else:
    path = "/etc/stratumgs.conf"
    if os.path.exists(path):
        _CONFIG.read(path)


def get(section, option):
    """
        Get a value from the configuration.

        :param section: The section in the config the value is in.
        :type section: str
        :param option: The option within the section.
        :type option: str
        :returns: The value for the configuration parameter, or the default
                  value if no explicit value was set.
    """

    if section in _CONFIG_VALUES:
        if option in _CONFIG_VALUES[section]:
            type_fn, default = _CONFIG_VALUES[section][option]
            return type_fn(_CONFIG.get(section, option, fallback=default))
    return None
