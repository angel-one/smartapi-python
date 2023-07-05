from setuptools import setup, find_packages

about={}
with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = [
        "requests>=2.18.4",
        "six>=1.11.0",
        "python-dateutil>=2.6.1"
    ]

setup(
    name="smartapi-python",
    version="1.3.4",
    author="ab-smartapi",
    author_email="smartapi.sdk@gmail.com",
    description="Angel Broking openApi integration",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/angelbroking-github/smartapi-python",
    packages=["smartapi"],
    install_requires=requirements,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries"
    ],
)
