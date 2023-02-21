from setuptools import setup

setup(
    name="dbcl",
    version="0.1.24",
    description="A database command line interface that is engine-agnostic.",
    author="Kris Steinhoff",
    url="https://github.com/ksofa2/dbcl",
    download_url="https://github.com/ksofa2/dbcl/archive/0.1.12.tar.gz",
    keywords=["db", "command-line-tool"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Development Status :: 3 - Alpha",
        "Topic :: Database",
        "Topic :: Database :: Front-Ends",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["dbcl"],
    entry_points={
        "console_scripts": ["dbcl=dbcl.command_line:command_loop"],
    },
    include_package_data=True,
    install_requires=[
        "sqlalchemy>=1.2.8<2",
        "prompt_toolkit>=2.0.0,<3",
        "pygments>=2.2.0,<3",
        "terminaltables>=3.1.0,<4",
    ],
    setup_requires=[
        "pytest-runner",
    ],
    tests_require=[
        "pytest",
        "pytest-mock",
    ],
)
