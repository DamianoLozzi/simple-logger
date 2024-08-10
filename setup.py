from setuptools import setup, find_packages
setup(
    name='simple_logger',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'configparser',
        'coloredlogs',
        'colorama',
    ],
    description='A simple logger for Python',
    author='DamianoLozzi',
    author_email='damianolozzi1989@gmail.com',
    url='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.7',
)