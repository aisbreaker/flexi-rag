

def model_to_module_and_class(model: str) -> tuple[str, str]:
    """
    Get the module and class name of a model instance.

    Args:
        model: module name dot class name

    Returns:
        (str, str): module name, class name
    """
    result =  model.rsplit('.', 1)
    return (result[0], result[1])
