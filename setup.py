from distutils.core import setup

setup(
    name='pp_api',
    version='profit-v11',
    packages=['pp_api', 'pp_api.server_data'],
    license='MIT',
    requires=open('requirements.txt', 'r').read().split()
)