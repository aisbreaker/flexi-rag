import yaml
import os

import logging

logger = logging.getLogger(__name__)

#
# This logic is used to load and merge configurations from two YAML files.
#
# The default configuration is loaded from 'default-values.yaml'
# and the  specific configuration is loaded from 'values.yaml'.
# The specific configuration overrides the default configuration.
#
# Any of this configuratin can be overridden by setting an appropriate environment variable.

def load_yaml_file(file_path):
    """Load YAML file from the given path."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def merge_configs(default_config, override_config):
    """Merge two configurations with the override_config taking precedence."""
    def merge_dicts(default_dict, override_dict):
        merged_dict = default_dict.copy()
        if override_dict is not None and hasattr(override_dict, "items") is True:
            for key, value in override_dict.items():
                if key in merged_dict and isinstance(merged_dict[key], dict) and isinstance(value, dict):
                    merged_dict[key] = merge_dicts(merged_dict[key], value)
                elif key in merged_dict and isinstance(merged_dict[key], list) and isinstance(value, list):
                    merged_dict[key] = merged_dict[key] + value
                else:
                    merged_dict[key] = value
            return merged_dict
        else:
            return default_dict

    return merge_dicts(default_config, override_config)


def overwrite_with_env_variables(config, key_prefix=""):
    """Overwrite configuration values with environment variables if they exist.

    Args:
        config (dict): The configuration dictionary to be overwritten.
        key_prefix (str, optional): The prefix to be added to the keys when checking for environment variables.
            For example, if the key_prefix is "database.", the environment variable for the (nested) key "host" would be "DATABASE_HOST".
            Defaults to "".

    Returns:
        dict: The updated configuration dictionary.
    """
    for key, value in config.items():
        try:
            # assuming environment variables are uppercase versions of the config keys
            env_var = f"{key_prefix}{key}".upper().replace(".", "_")

            # single value
            if env_var in os.environ:
                # Convert environment variable string to the correct type (e.g., int, float, bool)
                if isinstance(value, int):
                    config[key] = int(os.environ[env_var])
                elif isinstance(value, float):
                    config[key] = float(os.environ[env_var])
                elif isinstance(value, bool):
                    config[key] = bool(os.environ[env_var])
                else:
                    # default to string
                    config[key] = os.environ[env_var]
            # nested value
            elif isinstance(value, dict):
                config[key] = overwrite_with_env_variables(value, f"{key_prefix}{key}.")
            # list
            elif isinstance(value, list):
                config[key] = [overwrite_with_env_variables(item, f"{key_prefix}{key}.") if isinstance(item, dict) else item for item in value]
        except Exception as e:
            logger.error(f"Error while overwriting config with environment variables: key_prefix='{key_prefix}', key='{key}', (old)value='{value}', error={e}", e)
    return config

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
