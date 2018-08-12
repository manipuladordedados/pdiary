#!/usr/bin/env python3

from setuptools import find_packages, setup

setup(
    name="pdiary",
    version="0.80",
    description="A simple terminal diary journal application written in Python",
    keywords="diary pdiary journal terminal python",
    author="Valter Nazianzeno",
    author_email="manipuladordedados@gmail.com",
    url="https://github.com/manipuladordedados/pdiary",
    packages=["pdiary", "pdiary.lib",],
    package_data={"": ["LICENSE", "README.md", "CHANGELOG.md", "AUTHORS"]},
    install_requires=[
        "npyscreen>=4.10.5",
        "peewee>=2.8.3",
        "pysqlcipher3>=1.0.2",
    ],
    license="GNU GPLv3",
    classifiers=["License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                   "Operating System :: POSIX :: Linux",
                   "Programming Language :: Python :: 3 :: Only",
                 ],
    entry_points={
        "console_scripts": ["pdiary = pdiary.main:main"]
      },
)
