from setuptools import setup, find_packages

setup(
    name = 'watchmaker',
    version = '0.1',
    packages = find_packages(where='src'),
    package_dir = { "" : "src"},
    include_package_data = True,
    include_requires = [
        "botocore",
        "boto3",
        "PyYAML"
    ]
)
