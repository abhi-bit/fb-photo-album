import sys
from setuptools import setup

PY3 = sys.version_info[0] == 3

install_requires = [
    'six',
    'anyjson',
    ]
extra = {}
if PY3:
    extra['use_2to3'] = True
else:
    install_requires.extend([
            'poster',
            ])

if sys.version_info[0] == 2 and sys.version_info[1] == 5:
    install_requires.extend([
            'simplejson',
            ])


setup(
    name='snaptest',
    version='0.1',
    description='App to pull up fb photos to wedding snap',
    author='Abhishek',
    author_email='singhabhishek.bit@gmail.com',
    url='https://www.facebook.com/abhishek1349',
    package_dir={'': 'src'},
    py_modules=[
        'snaptest',
    ],
    license="Apache 2.0",
    install_requires=install_requires,
    zip_safe=True,
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
        ],
    test_suite = "snaptest.test_suite",
    entry_points = """
      [console_scripts]
      snaptest = snaptest:shell
    """,
    **extra
    )
