from setuptools import setup, find_packages

setup(
    name="data_validator",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "functions-framework==3.*",
        "google-cloud-pubsub==2.*",
        "flask==2.*",
        "google-cloud-storage>=2.7.0",
        "google-cloud-logging>=3.5.0",
        "python-json-logger>=2.0.7",
        "pytest>=7.0.0",
        "pytest-mock>=3.10.0",
    ],
) 