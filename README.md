# cy-stubgen

This is a script for generating stub files from compiled Cython.

This tool uses the [mypy stubgen](https://github.com/python/mypy/blob/master/mypy/stubgen.py) module to generate stub files from compiled Cython files.
The stub files are generated in the same directory as the Cython files.

This is not a complete replacement for manual `.ipy` file generation, and does not support all features of the Cython compiler. However, it is a useful
script for prototyping simple Cython projects and allows most IDEs to use the stub files for type checking and autocompletion.

## Usage

```bash
python -m pip install Cython mypy setuptools
```

Then, move the `cy_stubgen.py` file to the root of your project directory. It can then be used as:

```python
from cy_stubgen import cy_stubgen

cy_stubgen("test_project")
```

Where `test_project` is the name of the directory containing the Cython files.
