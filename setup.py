from distutils.core import setup

setup(
    name='ekstrakto',
    version='0.1dev',
    packages=['ekstrakto'],
    install_requires=[
        'Pillow',
        'scipy',
        'scikit-learn',

        # fixes an issue in scikit-learn
        # https://github.com/scikit-learn/scikit-learn/issues/12226
        'cloudpickle'
    ],
    entry_points = {
        'console_scripts': [
            'ek=ekstrakto.cli:entrypoint',
        ]
    },
    license='MIT',
    long_description=open('README.md').read(),
)