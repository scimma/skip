import os
from setuptools import setup, find_packages

# read in README
this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, 'README.md'), 'rb') as f:
    long_description=f.read().decode().strip()

setup(
    name='skip',
    description='Django REST api to Hop Alerts Database',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://www.github.com/scimma/skip',
    author='Lindy Lindstrom, David Collom',
    author_email='{llindstrom, dcollom}@lco.global',
    license='BSD 3-Clause',
    packages=find_packages(),
    python_requires='>=3.6.*',
    install_requires=[
        'astropy>=4.2',
        'beautifulsoup4>=4.9',
        'boto3~=1.17',
        'confluent_kafka>=1.6',
        'Django>=3.1',
        'django-cors-headers>=3.7',
        'django-extensions>=3.1',
        'django-filter>=2.4',
        'djangorestframework>=3.12',
        'gracedb-sdk~=0.1',
        'healpy>=1.14',
        "hop-client >= 0.4",
        'numpy>=1.20',
        'psycopg2>=2.8',
        'python-dateutil>=2.8',
        'skip-django',
        'whitenoise>=5.2',
        'voevent-parse~=1.0',
    ],
    dependency_links=['git+git://github.com/TOMToolkit/skip-django.git#egg=skip-django'],
    extras_require={
        'dev': ['pytest', 'pytest-console-scripts', 'pytest-cov', 'flake8', 'flake8-black'],
        'docs': ['sphinx', 'sphinx_rtd_theme', 'sphinxcontrib-programoutput'],
        'docker': ['gunicorn[gevent]']
    },
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Physics',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'License :: OSI Approved :: BSD License',
    ],

)
