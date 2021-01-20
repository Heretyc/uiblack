import os.path
from setuptools import setup

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

setup(
    name="uiblack",
    version="1.0.0",
    description="Streamlined cross-platform Textual UI",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/BlackburnHax/uiblack",
    author="Brandon Blackburn",
    author_email="contact@bhax.net",
    license="Apache 2.0",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=["uiblack"],
    include_package_data=True,
    install_requires=[
        "blessed"
    ]
)
