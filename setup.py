from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pybsrnqc',
    version='0.1.66',
    description='Package to study BSRN data and their quality control',
    url='https://github.com/LE2P/PyBsrnQC/tree/main/pybsrnqc',
    author='Maelle Baronnet',
    author_email='maelle.baronnet@gmail.com',
    license='MIT',
    include_package_data=True,
    packages=['pybsrnqc'],
    install_requires=['pandas',
                      'numpy>=1.17.4',
                      'matplotlib>=3.3.2',
                      'pvlib>=0.8.0',
                      'bokeh>=2.2.3',
                      'cryptography>=2.8',
                      'pytz>=2019.3'
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
