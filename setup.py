import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="supermarket-gmcadams1", # Replace with your own username
    version="1.0.0",
    author="Gregory McAdams",
    author_email="gmcadams1@comcast.net",
    description="Supermarket POS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gmcadams1/supermarket",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)