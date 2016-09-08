from setuptools import setup, find_packages

setup(name='esgissue-client',
      version='0.1',
      description='Local client to create, update, close and retrieve ESGF issues',
      author='Levavasseur Guillaume',
      author_email='glipsl@ipsl.jussieu.fr',
      url='https://github.com/ES-DOC/esdoc-errata-client',
      packages=find_packages(),
      include_package_data=True,
      install_requires=['requests>=2.9.1',
                        'jsonschema>=2.4.0',
                        'requests'
                        ],
      platforms=['Unix'],
      zip_safe=False,
      entry_points={'console_scripts': ['esgissue=esgissue.esgissue:run']},
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: System Administrators',
                   'Natural Language :: English',
                   'Operating System :: Unix',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Software Development :: Build Tools']
      )
