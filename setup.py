from distutils.core import setup

setup(
    name='pp_api',
    version='profit-v12',
    packages=['pp_api'],
    license='MIT',
    requires=open('requirements.txt', 'r').read().split()
)