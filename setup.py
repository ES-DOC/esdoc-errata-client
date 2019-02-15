from setuptools import setup, find_packages
from esgissue.constants import VERSION_NUMBER
setup(name='esgissue-client',
      version=VERSION_NUMBER,
      description='Local client to create, update, close and retrieve ESGF issues',
      author='Atef Ben Nasser',
      author_email='abennasser@ipsl.fr',

      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'Operating System :: Unix',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Scientific/Engineering',
          'License :: OSI Approved :: MIT License',
      ],

      url='https://github.com/ES-DOC/esdoc-errata-client',
      packages=find_packages(),
      include_package_data=True,
      install_requires=['requests',
                        'jsonschema',
                        'functools32',
                        'simplejson',
                        'jsonschema',
                        'argparse',
                        'repoze.lru',
                        'pyDes',
                        'pbkdf2'
                        ],
      platforms=['Unix'],
      zip_safe=False,
      entry_points={'console_scripts': ['esgissue=esgissue.esgissue:run']},
      )
