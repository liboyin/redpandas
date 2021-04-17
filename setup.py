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
    install_requires=['numpy', 'pandas', 'redis'],
    extras_require={
        'dev': ['mypy', 'pytest', 'pytest-cov', 'pytest-randomly'],
    },
)
