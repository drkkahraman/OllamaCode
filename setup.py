from setuptools import setup

setup(
    name="ollamacode",
    version="0.1.0",
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
    author="Your Name",
    description="A powerful AI-powered terminal assistant connecting Groq and Ollama.",
    python_requires=">=3.8",
)
