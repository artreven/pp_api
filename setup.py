from distutils.core import setup

requirements = []

with open('requirements.txt', 'r') as f:
    for line in f:
        requirements.append(str(line.strip()))

print("Requirements:")
print(requirements)

setup(
    name='pp_api',
    version='0.1dev',
    packages=['pp_api', 'pp_api.server_data'],
    license='MIT',
    requires=requirements
)