from setuptools import setup

setup(
    name='pysh-commands-command',
    version='0.1',
    py_modules=['command'],
    include_package_data=True,
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        command=command:cli
    ''',
)
