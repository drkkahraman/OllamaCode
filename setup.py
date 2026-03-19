from setuptools import setup, find_packages

setup(
    name="ollamacoder",
    version="1.2.3",
    packages=find_packages(),
    install_requires=[
        "requests",
        "rich",
        "psutil"
    ],
    entry_points={
        "console_scripts": [
            "ollamacoder_py=ollamacode.main:main",
        ],
    },
    author="drkkahraman",
    description="OllamaCoder: AI-Powered Autonomous Terminal Agent (Python Edition)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/drkkahraman/OllamaCoder",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
