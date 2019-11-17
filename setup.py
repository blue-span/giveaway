from setuptools import setup
from setuptools.command.install import install
import pathlib
import sys


class compile_sass_preinstall(install):
    def run(self):
        import sass
        setup_dir = pathlib.Path(sys.modules[__name__].__file__).parent
        input_path = setup_dir / "style" / "bluespan.scss"
        output_path = setup_dir / "giveaway" / "static" / "css" / "bluespan.css"
        output_path.parent.mkdir(exist_ok=True)
        with output_path.open("w") as f:
            out = sass.compile(filename=str(input_path))
            f.write(out)
        print("compiled", str(input_path), "->", str(output_path))
        super().run()


setup(
    setup_requires=['setuptools_scm', 'libsass'],
    use_scm_version=True,
    cmdclass={
        'install': compile_sass_preinstall,
    },
)
