from distutils.core import setup

setup(
    name='ekstrakto',
    version='0.1dev',
    packages=['ekstrakto'],
    scripts=['bin/ek'],
    license='MIT',
    long_description=open('README.md').read(),
)