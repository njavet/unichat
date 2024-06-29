from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(
    name='unichat',
    version='0.1.0',
    author='Noe Javet',
    description='QT Desktop chat client that unifies telegram and whatsapp',
    url='https://github.zhaw.ch/UniChat/unichat',
    packages=find_packages(),
    package_data={
        'unichat': ['assets/icons/*.png',
                    'assets/images/*png',
                    'assets/stylesheets/*.qss'],
    },
    install_requires=requirements
)

