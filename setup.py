from setuptools import setup

setup(
    name='pyqcbsrn',
    version='0.1.4',
    description='Package to study BSRN data and their quality control',
    url='https://github.com/LE2P/PyBsrnQC/tree/main/pyqcbsrn',
    author='Maelle Baronnet',
    author_email='maelle.baronnet@gmail.com',
    license='MIT',
    packages=['pyqcbsrn'],
    install_requires=['pandas',
                      'numpy',
                      'matplotlib.pyplot'
                      ],

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
