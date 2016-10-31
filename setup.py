from setuptools import setup, find_packages
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session=False)

version = '0.0.1'


setup(
    name='pycmd',
    version=version,
    description="""sth.""",
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Libraries :: Python Modules",
        "Environment :: Test Environment",
    ],
    keywords='',
    author='ningskyer',
    author_email='ningskyer@qq.com',
    packages=find_packages(),
    entry_points='''
    [console_scripts]
    pycmd=pycmd.cli
    ''',
    license='GNU GPL V3',
    install_requires=[str(ir.req) for ir in install_reqs],
    include_package_data=True,
    zip_safe=False,
)
