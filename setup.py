import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Smart Album Creator",
    version = "0.0.1",
    author = "Abhishek Singh",
    author_email = "singhabhishek.bit@gmail.com",
    description = ("Pull photos from FB, push to Wedding Snap"),
    license = "BSD",
    keywords = "Wedding Snap FB",
    url = "http://graph.facebook.com/abhishek1349",
    packages=['snaptest'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
