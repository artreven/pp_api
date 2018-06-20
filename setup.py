from distutils.core import setup

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup(
    name='pp_api',
    version='0.1dev',
    packages=['pp_api'],
    license='MIT',
    requires=requirements
)