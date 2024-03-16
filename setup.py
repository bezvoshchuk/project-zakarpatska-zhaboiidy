from setuptools import setup, find_packages

setup(
    name='cli_bot',
    version='1.0',
    author='Project Team 1',
    description='Project Zakarpatski Zhaboiidy',
    url='https://github.com/bezvoshchuk/project-zakarpatski-zhaboiidy',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        "prompt_toolkit"
    ],
    entry_points={
        'console_scripts': [
            'cli_bot=source.cli_bot:main',  
        ],
    },
)