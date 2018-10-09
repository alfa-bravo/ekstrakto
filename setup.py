from distutils.core import setup

setup(
    name='ekstrakto',
    version='0.1dev',
    packages=['ekstrakto'],
    console_scripts=['ek=ekstrakto.cli:entrypoint'],
    license='MIT',
    long_description=open('README.md').read(),
)