from setuptools import setup, find_packages

"""
setup(
    name="mt5exchange",
    version="0.1.4",
    packages=find_packages(),
    install_requires=[
        "MetaTrader5",
        "pandas"
    ],
    author="Eduardo Barata",
    description="Interface Python personalizada para operações com MetaTrader 5",
    url="https://github.com/edubarata/mt5exchange",
)
"""

setup(
    name="mt5exchange",
    version="0.1.5",
    packages=find_packages(),
    install_requires=["pandas"],          # MetaTrader5 sai daqui
    extras_require={
        "windows": ["MetaTrader5"],       # só instala quando precisar (Windows)
    },
    author="Eduardo Barata",
    description="Interface Python personalizada para operações com MetaTrader 5",
    url="https://github.com/edubarata/mt5exchange",
)