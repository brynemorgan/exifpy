from setuptools import setup, find_packages
# import exifread

readme_file = open("README.rst", "rt").read()

dev_requirements = [
    "mypy==0.931",
    "pylint==2.12.2",
]

setup(
    name="ExifRead",
    version='3.1.0',
    author="Ianaré Sévi",
    author_email="ianare@gmail.com",
    packages=find_packages(),
    install_requires=[
        'rdflib>=6.3.2'
        ],
    scripts=["EXIF.py"],
    url="https://github.com/ianare/exif-py",
    license="BSD",
    keywords="exif image metadata photo",
    description="Read Exif metadata from tiff and jpeg files.",
    long_description=readme_file,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
    ],
    extras_require={
        "dev": dev_requirements,
    },
)
