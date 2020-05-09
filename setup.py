import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="twsyncer",
    version="0.0.3",
    author="Stan Bogatkin",
    author_email="sbog@sbog.ru",
    description="Tool to sync Taswarrior and remote task trackers",
    entry_points={
        "console_scripts": [
            "twsyncer = twsyncer.main:main",
        ]
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/twsyncer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
