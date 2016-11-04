from setuptools import setup

setup(
    name='pycmd-commands-shell',
    version='0.1',
    py_modules=['shell'],
    include_package_data=True,
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        shell=shell:cli
    ''',
)
