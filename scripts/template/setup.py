from setuptools import setup

setup(
    name='pycmd-commands-template',
    version='0.1',
    py_modules=['template'],
    include_package_data=True,
    install_requires=[
        'click'
    ],
    entry_points='''
        [console_scripts]
        template=template:cli
    ''',
)
