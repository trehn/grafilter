from setuptools import setup, find_packages


setup(
    author="Torsten Rehn",
    author_email="torsten@rehn.email",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Database :: Front-Ends",
        "Topic :: Internet :: Log Analysis",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring",
    ],
    description="Helps you explore and graph all your metrics as a supplement to dashboard solutions like Grafana",
    entry_points={
        'console_scripts': [
            "grafilter=grafilter.cli:main",
        ],
    },
    include_package_data=True,
    install_requires=[
        "Flask",
        "gunicorn",
        "parsedatetime >= 1.4",
        "requests >= 1.0.0",
    ],
    keywords=[
        "graph",
        "influxdb",
        "metrics",
    ],
    license="GPLv3",
    name="grafilter",
    packages=find_packages(),
    url="https://github.com/trehn/grafilter",
    version="0.1.0",
    zip_safe=False,
)
