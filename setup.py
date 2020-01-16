from setuptools import setup, find_packages
setup(
    name="json_conf_autoref",
    version="0.0.4",
    packages=find_packages(),
    scripts=["start_tests.py"],

    # metadata to display on PyPI
    author="Andre Carneiro",
    author_email="andregarciacarneiro@gmail.com",
    description="JSON config parser with variable reference's handler",
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
    test_suite='tests'

    # could also include long_description, download_url, etc.
)