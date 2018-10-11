from distutils.core import setup

setup(
    name='ekstrakto',
    version='0.1dev',
    packages=['ekstrakto'],
    install_requires=[
        'Pillow==5.3.0',
        'scipy==1.1.0',
        'scikit-learn==0.20.0',

        # fixes an issue in scikit-learn
        # https://github.com/scikit-learn/scikit-learn/issues/12226
        'cloudpickle==0.5.6'
    ],
    entry_points = {
        'console_scripts': [
            'ek=ekstrakto.cli:entrypoint',
        ]
    },
    license='MIT',
    long_description=open('README.md').read(),
)