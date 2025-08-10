# -*- coding: utf-8 -*-
import importlib
import os
import sys
import types
from glob import glob
from os.path import abspath, basename, exists, join, splitext

import pandas_ta
from pandas_ta._typing import DictLike



def bind(name: str, fn: types.FunctionType, method: types.MethodType = None):
    """Bind

    Helper function to bind the function and class method defined in a custom
    indicator module to the active pandas_ta instance.

    Parameters:
        name (str): The name of the indicator within pandas_ta
        fn (types.FunctionType): The indicator function
        method (types.MethodType): The class method corresponding to the passed function
    """
    setattr(pandas_ta, name, fn)
    setattr(pandas_ta.AnalysisIndicators, name, method)


def create_dir(path: str, categories: bool = True, verbose: bool = True):
    """Create Dir

    Sets up a suitable folder structure for working with custom indicators.
    Use it **once** to setup and initialize the custom folder.

    Parameters:
        path (str): Indicator directory full path
        categories (bool): Create category sub-folders
        verbose (bool): Verbose output
    """

    # ensure that the passed directory exists / is readable
    if not exists(path):
        os.makedirs(path)
        if verbose:
            print(f"[i] Created main directory '{path}'.")

    # list the contents of the directory
    # dirs = glob(abspath(join(path, '*')))

    # optionally add any missing category subdirectories
    if categories:
        for _ in [*pandas_ta.Category]:
            d = abspath(join(path, _))
            if not exists(d):
                os.makedirs(d)
                if verbose:
                    dirname = basename(d)
                    print(f"[i] Created an empty sub-directory '{dirname}'.")


def get_module_functions(module: types.ModuleType) -> DictLike:
    """Get Module Functions

    Returns a dictionary with the mapping: "name" to a _function_.

    Parameters:
        module (types.ModuleType): python module

    Returns:
        (DictLike): Returns a dictionary with the mapping: "name" to a _function_

    Example:
        Example return
        ```py
        {
            "func1_name": func1,
            "func2_name": func2, # ...
        }
        ```
    """
    module_functions = {}

    for name, item in vars(module).items():
        if isinstance(item, types.FunctionType):
            module_functions[name] = item

    return module_functions


def import_dir(path: str, verbose: bool = True):
    """Import Dir

    Import a directory of custom (proprietary) indicators into Pandas TA.

    Parameters:
        path (str): Full path to indicator directory.
        verbose (bool): Output process to STDOUT.
    """
    # ensure that the passed directory exists / is readable
    if not exists(path):
        print(f"[X] Unable to read the directory '{path}'.")
        return

    # list the contents of the directory
    dirs = glob(abspath(join(path, "*")))

    # traverse full directory, importing all modules found there
    for d in dirs:
        dirname = basename(d)

        # only look in directories which are valid pandas_ta categories
        if dirname not in [*pandas_ta.Category]:
            if verbose and dirname not in ["__pycache__", "__init__.py"]:
                print(
                    f"[i] Skipping the sub-directory '{dirname}' since it's not a valid pandas_ta category."
                )
            continue

        # for each module found in that category (directory)...
        for module in glob(abspath(join(path, dirname, "*.py"))):
            module_name = splitext(basename(module))[0]
            if module_name not in ["__init__"]:
                # ensure that the supplied path is included in our python path
                if d not in sys.path:
                    sys.path.append(d)

                # (re)load the indicator module
                module_functions = load_indicator_module(module_name)

                # figure out which of the modules functions to bind to pandas_ta
                _callable = module_functions.get(module_name, None)
                _method_callable = module_functions.get(f"{module_name}_method", None)

                if _callable == None:
                    print(
                        f"[X] Unable to find a function named '{module_name}' in the module '{module_name}.py'."
                    )
                    continue
                if _method_callable == None:
                    missing_method = f"{module_name}_method"
                    print(
                        f"[X] Unable to find a method function named '{missing_method}' in the module '{module_name}.py'."
                    )
                    continue

                # add it to the correct category if it's not there yet
                if module_name not in pandas_ta.Category[dirname]:
                    pandas_ta.Category[dirname].append(module_name)

                bind(module_name, _callable, _method_callable)
                if verbose:
                    print(
                        f"[i] Successfully imported the custom indicator '{module}' into category '{dirname}'."
                    )


def load_indicator_module(name: str) -> dict:
    """
     Helper function to (re)load an indicator module.

    Returns:
        dict: module functions mapping
        ```{
            "func1_name": func1,
            "func2_name": func2, # ...
        }```

    """
    try:
        module = importlib.import_module(name)
    except Exception as ex:
        print(f"[X] An error occurred when attempting to load module {name}: {ex}")
        sys.exit(1)

    # reload to refresh previously loaded module
    module = importlib.reload(module)
    return get_module_functions(module)
