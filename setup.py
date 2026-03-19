import os
from setuptools import setup, find_packages

setup(
    name="ollamacode",
    version="1.1.1",
    author="Doruk",
    description="Modular AI Terminal Assistant with autonomous features",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/drkkahraman/OllamaCode",
    packages=find_packages(),
    install_requires=[
        "requests",
        "psutil",
        "python-dotenv",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "ollamacode=ollamacode.main:main",
        ],
    },
    python_requires=">=3.8",
)
