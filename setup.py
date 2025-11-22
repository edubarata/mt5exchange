from setuptools import setup, find_packages

setup(
    name="mt5exchange",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "MetaTrader5",
        "pandas"
    ],
    author="Eduardo Barata",
    description="Interface Python personalizada para operações com MetaTrader 5",
    url="https://github.com/edubarata/mt5exchange",
)
