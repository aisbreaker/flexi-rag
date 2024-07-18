import yaml
import os

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
  return config

def print_config(config, indent=0):
  """Print the configuration dictionary with proper indentation."""

  if config is not None and hasattr(config, "items") is True:
    for key, value in config.items():
      if isinstance(value, dict):
        print("  " * indent + f"{key}:")
        print_config(value, indent + 1)
      else:
        if "pass" in key.lower() or "token" in key.lower():
          print("  " * indent + f"{key}: {'*' * len(str(value))}")
        else:
          print("  " * indent + f"{key}: {value}")

def main():
    # load the default configuration
    default_config = load_yaml_file('default-values.yaml')
    print("default_config:")
    print_config(default_config)

    # load the specific configuration
    values_config = load_yaml_file('values.yaml')
    
    # merge the configurations
    merged_config = merge_configs(default_config, values_config)
    print("merged_config:")
    print_config(merged_config)

    # Overwrite with environment variables
    final_config = overwrite_with_env_variables(merged_config)
    
    # use the final configuration
    print("Final Configuration:")
    print_config(final_config)

if __name__ == "__main__":
    main()