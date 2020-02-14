from distutils.core import setup

setup(
    name='ekstrakto',
    version='0.2dev',
    packages=['ekstrakto'],
    install_requires=[
        'numpy',
        'pillow',
        'kdtree',
    ],
    entry_points = {
        'console_scripts': [
            'ek=ekstrakto.cli:entrypoint',
        ]
    },
    license='MIT',
    long_description=open('README.md').read(),
)