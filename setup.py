import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="twsyncer",
    version="0.0.2",
    author="Stan Bogatkin",
    author_email="sbog@sbog.ru",
    description="Tool to sync Taswarrior and remote task trackers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/twsyncer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
