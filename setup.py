from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='rancher-env',
      version='0.1',
      description='Manage rancher enviroments in rancher-cli',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Rancher CLI :: Environments',
      ],
      keywords='rancher rancher-cli environments',
      url='http://github.com/jorgenbl/rancher-env',
      author='Jørgen Blakstad',
      author_email='jorgenbl@gmail.com',
      license='MIT',
      packages=['rancher-env'],
      install_requires=[
          'beautifultable',
      ],
      zip_safe=False)