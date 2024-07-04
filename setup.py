from setuptools import setup, find_packages

setup(
    name="cloudysetup",
    version="0.1",
    packages=find_packages(include=["cloudysetup", "cloudysetup.*"]),
    include_package_data=True,
    install_requires=[
        "click",
        "requests",
        "boto3",
        "python-dotenv",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "cloudysetup-cli=cloudysetup.cli_tool.cli:cli",
        ],
    },
)
