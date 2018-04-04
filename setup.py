from distutils.core import setup

setup(
    name='pp_api',
    version='0.1dev',
    packages=['pp_api'],
    license='MIT',
    requires=open('requirements.txt', 'r').read().split()
)