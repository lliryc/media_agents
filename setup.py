"""Python setup.py for project_name package"""
import io
import os
from setuptools import find_packages, setup


def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("media_agents", "VERSION")
    '0.1.0'
    >>> read("README.md")
    ...
    """

    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def read_requirements(path):
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]


setup(
    name="media_agents",
    version=read("media_agents", "VERSION"),
    description="Intelligent agent for journalists to find news leads in court decisions",
    url="https://github.com/lliryc/media_agents/",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Kirill Chirkunov",
    packages=find_packages(exclude=["tests", ".github", "state", "insights"]),
    install_requires=read_requirements("requirements.txt"),
    entry_points={
        "console_scripts": ["project_name = media_agents.__main__:main"]
    },
)
