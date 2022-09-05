from distutils.core import setup


setup(
    name='stocks',
    version='0.1.0',
    description='Library for analyzing stocks',
    author='Hank Adler',
    packages=[
        'collector',
        'daemon',
        'dparser',
        'forecaster',
        'indicators',
        'plotter',
        'utils',
        'xport'
    ],
)
