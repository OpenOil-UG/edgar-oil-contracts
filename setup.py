from setuptools import setup, find_packages

setup(
    name='dissect',
    version='0.1',
    description="disSECt -- tools to get info from SEC filings, as well as SEDAR etc",
    long_description="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    keywords='',
    author='',
    author_email='daniel@ohuiginn.net',
    url='http://openoil.net',
    license='MIT',
    packages=['dissect'], #find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=[],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points={},
    tests_require=[]
)
