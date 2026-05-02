from setuptools import setup, find_packages

setup(
    name="ollamacode",
    version="1.3",
    packages=find_packages(),
    install_requires=[
        "requests",
        "rich",
        "psutil"
    ],
    entry_points={
        "console_scripts": [
            "ollamacode=ollamacode.main:main",
            "llam=ollamacode.main:main",
        ],
    },
    author="drkkahraman",
    description="OllamaCode: AI-Powered Autonomous Terminal Agent (Python Edition)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/drkkahraman/OllamaCode",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
