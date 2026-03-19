import os
from setuptools import setup, find_packages

setup(
    name="ollamacode",
    version="3.1.0",
    author="Doruk",
    description="High-performance AI Terminal Agent powered by Groq and Ollama",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/doruk/ollamacode",
    py_modules=["ollamacode"],
    install_requires=[
        "requests",
        "psutil",
        "python-dotenv",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "ollamacode=ollamacode:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
