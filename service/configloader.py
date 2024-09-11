"""
Settings are loaded from YAML files:
- default-config.yaml
- config.yaml

These settings can be overwritten by environment variables:
Examples:
  export RAG_FOO=BAR                      # string value
                                          # with RAG_ prefix

  export RAG_NESTED__LEVEL__KEY=1         # Double underlines
                                          # denotes nested settings
                                          # nested = {
                                          #     "level": {"key": 1}
                                          # }
(More details on this: https://www.dynaconf.com/#on-env-vars )
                                          
The internal implementation is based on the Dynaconf library,
but special Dynaconf features/syntax are not allowed to be used
because the internal implementation can change in the future.

Hydra/omegaconf is not used internally
because it does not support overwriting by environment variables.
"""

import json
from typing import Dict
import yaml
import os

import logging

logger = logging.getLogger(__name__)

from dynaconf import Dynaconf

settings = Dynaconf(
    #root_path="/data/aisbreaker-workspace/hapkecom-github/flexi-rag/",
    settings_files=[
        "default-config.yaml",
        "config.yaml",
        #".secrets.yaml",
    ],
    merge_enabled=True,
    #environments=True,
    #env_switcher="MYAPP_MODE",         # `export MYAPP_MODE=production`
    envvar_prefix="RAG"
)

_no_default = "_NO_DEFAULT_VALUE_PLACEHOLDER_sdknfcw9845cvnhkjrvzh6"

def deep_get(dict: Dict, keys_str: str, default_value: any = _no_default) -> any:
    """Get a value from a nested dictionary by a dot-separated key string."""
    keys = keys_str.split(".")
    dictOrResult = dict
    used_keys = ""
    for key in keys:
        # try to access value
        used_keys += key
        dictOrResult = dictOrResult.get(key)
        if dictOrResult is None:
            # key not found
            if default_value == _no_default:
                raise KeyError(f"Key '{used_keys}' not found in dictionary")
            else:
                return default_value
        # key found

        # prepare next loop
        used_keys += "."

    # done
    return dictOrResult



# Accessing a setting . trigger loading now to see config errors here
logger.info(f"name={settings.name}")
logger.info(f"config.crawling.enabled={settings.config.crawling.enabled}")
logger.info(f"test.value={settings.test.value}")
logger.info(f"test.value2={settings.test.value2}")



def config_str(config, indent=0) -> str:
    """Create a formatted multiline-string of the configuration dictionary with proper indentation."""

    result = ""
    if config is not None and hasattr(config, "items") is True:
        for key, value in config.items():
            linestart = "\n" + ("  " * indent)
            if isinstance(value, dict):
                result += linestart + f"{key}:"
                result += config_str(value, indent + 1)
            else:
                if "pass" in key.lower() or "token" in key.lower():
                    result += linestart + f"{key}: {'*' * len(str(value))}"
                else:
                    result += linestart + f"{key}: {value}"
    return result

logger.info("## Final Configuration:"+config_str(settings.as_dict()))

def main():
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(levelname)-8s %(filename)s:%(funcName)s() - %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    # load the default configuration
    default_config = load_yaml_file('default-values.yaml')
    logger.debug("default_config:"+str(default_config))

    # load the specific configuration
    values_config = load_yaml_file('values.yaml')
    
    # merge the configurations
    merged_config = merge_configs(default_config, values_config)
    logger.debug("merged_config:"+str(merged_config))

    # Overwrite with environment variables
    final_config = overwrite_with_env_variables(merged_config)
    
    # use the final configuration
    logger.info("## Final Configuration:"+config_str(final_config))

if __name__ == "__main__":
    main()
