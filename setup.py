import pathlib
from distutils.core import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="uiblack",
    version="1.0",
    packages=["uiblack"],
    url="https://github.com/BlackburnHax/uiblack",
    license="Apache 2.0",
    author="Brandon Blackburn",
    author_email="contact@bhax.net",
    description="Streamlined cross-platform Textual UI",
    long_description=README,
    long_description_content_type="text/markdown",
    install_requires=["blessed"],
)
