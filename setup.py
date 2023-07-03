from pathlib import Path
from setuptools import find_packages, setup

setup(
    name='redpandas',
    version='0.0.1',
    description='Cache pandas DataFrame to Redis by columns.',
    long_description=(Path(__file__).parent / 'README.md').read_text(),
    long_description_content_type='text/markdown',
    author='Libo Yin',
    author_email='liboyin830@gmail.com',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    # if Redis server is not installed already, add redis-server here
    install_requires=['numpy', 'pandas', 'redis'],
    extras_require={
        # mypy might also need types-redis types-setuptools
        'dev': ['mypy', 'pytest', 'pytest-cov', 'pytest-randomly'],
    },
)
