from setuptools import setup, find_packages

setup(
    name='grab_data',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'progress'
    ],
    entry_points='''
        [console_scripts]
        grab_data=src.cli:cli
    ''',
)
