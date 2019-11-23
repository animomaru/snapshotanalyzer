from setuptools import setup

setup(
    name='SnapshotAnalyzer',
    version='1.0',
    author='MP',
    author_email='frui.vita.trading@gmail.com',
    description='Tool to manage AWS EC2 snapshots',
    licence='GPLv3+',
    packages=['shotty'],
    url='https://github.com/mponan/snapshotanalyzer',
    install_requires=['click', 'boto3'],
    entry_points='''
        [console_scripts]
        shotty=shotty.shotty:cli
    ''',




)
