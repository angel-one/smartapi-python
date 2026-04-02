from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as readme_file:
    readme = readme_file.read()

requirements = [
    "requests>=2.18.4",
    "six>=1.11.0",
    "python-dateutil>=2.6.1"
]

setup(
    name="smartapi-python",
    version="1.5.5",
    author="ab-smartapi",
    author_email="smartapi.sdk@gmail.com",
    description="Angel Broking openAPI integration",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/angelbroking-github/smartapi-python",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Natural Language :: English",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries"
    ],
    python_requires='>=3.7',
)
