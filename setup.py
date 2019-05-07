import setuptools
from G.version import version

with open('README.md', 'r') as fh:
    long_description = fh.read()


setuptools.setup(
    name="G",
    version=version,
    author="wangxiangpeng",
    author_email="xiangpengm@126.com",
    description='A web framework package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xiangpengm/G",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'requests',
        'jinja2',
    ],

)
