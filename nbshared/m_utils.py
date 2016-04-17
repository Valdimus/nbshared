import importlib;

def create_instance(classToLoad, parameter):
    """
    Create a instance of a class with specified parameter
    :param classToLoad: Class to load
    :param parameter: parameter to specify to construtor class
    """
    tp_class=load_class(classToLoad);
    return tp_class(**parameter);

def load_class(classToLoad):
    """
    Load a class form string
    :param classToLoad: Class to load
    """
    [module_name, class_name] = classToLoad.rsplit(".", 1);
    module = importlib.import_module(module_name)
    return getattr(module, class_name);
