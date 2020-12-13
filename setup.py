from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="json_conf_autoref",
    version="0.1.5",
    packages=find_packages(),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    py_modules=['json_conf_autoref','exceptions'],

    # metadata to display on PyPI
    author="Andre Carneiro",
    author_email="andregarciacarneiro@gmail.com",
    description="JSON config parser with variable reference's handler",
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords="config json variable reference",
    url="https://github.com/bang/json-conf-autoref",   # project home page, if any
    project_urls={
        "Bug Tracker": "https://github.com/bang/json-conf-autoref/issues",
        "Documentation": "https://github.com/bang/json-conf-autoref/blob/master/README.md",
        "Source Code": "https://github.com/bang/json-conf-autoref",
    },
    classifiers=[
        "License :: OSI Approved :: Python Software Foundation License"
    ],


    # could also include long_description, download_url, etc.
)
