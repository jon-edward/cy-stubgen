import ast
import contextlib
import os
import pathlib
import tempfile
from typing import Callable, List, Optional, Union

from mypy import stubgen
from Cython.Build import cythonize
import setuptools


def cy_stubgen(
    path: Union[str, pathlib.Path],
    filter_func: Optional[Callable[[pathlib.Path], bool]] = None,
) -> None:
    """
    Generate stub files from Cython files as subdirectories of a given path.

    Args:
        path: The path to the Cython files or directory.
        filter_func: A function that takes a pathlib.Path and returns a bool. If the function returns False on a path, the stub file will not be generated.
    """

    files = list(pathlib.Path(path).glob("**/*.pyx"))

    if filter_func is not None:
        files = [f for f in files if filter_func(f)]
        
    _generate_pyi(files)


def _generate_pyi(files: List[pathlib.Path]) -> None:
    files = [pathlib.Path(p).absolute() for p in files]

    with tempfile.TemporaryDirectory() as tempdir:
        if len(files) == 0:
            return
        elif len(files) == 1:
            root_path = files[0].parent
        else:
            root_path = pathlib.Path(os.path.commonpath(files)).absolute()

        names_files = [
            (_path_as_module(file.relative_to(root_path)), file) for file in files
        ]

        extensions = [
            setuptools.Extension(
                name=name,
                sources=[str(file)],
            )
            for name, file in names_files
        ]

        setuptools.setup(
            ext_modules=cythonize(
                extensions,
                force=True,
                build_dir=tempdir,
                compiler_directives={
                    "embedsignature": True,
                    "embedsignature.format": "python",
                    "language_level": "3",
                },
            ),
            script_args=["build_ext", "--build-lib", tempdir],
        )

        with _cd(tempdir):
            for name, _ in names_files:
                stubgen.main(["-m", name, "--include-docstrings", "-o", str(root_path)])

        for file in files:
            file = file.with_suffix(".pyi")
            if file.exists():
                _transform_pyi(file)


def _path_as_module(path: pathlib.Path) -> str:
    return path.with_suffix("").as_posix().replace("/", ".")


@contextlib.contextmanager
def _cd(path: pathlib.Path):
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)


_excluded_function_names = {"__reduce__", "__reduce_cython__", "__setstate_cython__"}


class _PyiTransformer(ast.NodeTransformer):
    needs_incomplete = False

    def visit_AnnAssign(self, node):
        if node.target.id.startswith("__") and node.target.id.endswith("__"):
            return None
        if (
            isinstance(node.annotation, ast.Name)
            and node.annotation.id == node.target.id
        ):
            node.annotation.id = "Incomplete_"
            self.needs_incomplete = True
            return node
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if node.name in _excluded_function_names:
            return None
        return self.generic_visit(node)


def _transform_pyi(path: pathlib.Path) -> None:
    with open(path, "r") as f:
        before_content = f.read()

        ast_module = ast.parse(before_content)

        transformer = _PyiTransformer()
        transformer.visit(ast_module)

        after_content = ast.unparse(ast_module)

        if transformer.needs_incomplete:
            after_content = f"import typing\nIncomplete_ = typing.NewType('Incomplete_', typing.Any)\n\n{after_content}"

    with open(path, "w") as f:
        f.write(after_content)
