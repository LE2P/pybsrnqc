from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pyqcbsrn',
    version='0.1.18',
    description='Package to study BSRN data and their quality control',
    url='https://github.com/LE2P/PyBsrnQC/tree/main/pyqcbsrn',
    author='Maelle Baronnet',
    author_email='maelle.baronnet@gmail.com',
    license='MIT',
    include_package_data=True,
    packages=['pyqcbsrn'],
    install_requires=['pandas',
                      'numpy',
                      'matplotlib',
                      'pvlib',
                      'bokeh',
                      'cryptography',
                      'cassandra_driver',
                      'pytz'
                      ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
