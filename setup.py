from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pypm2",
    version="1.0.0",
    author="PyPM2 Team",
    author_email="dev@pypm2.com",
    description="Process Manager for Python Applications - A Python equivalent to PM2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypm2/pypm2",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "psutil>=5.8.0",
        "tabulate>=0.8.9",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "pypm2=pypm2.cli:main",
        ],
    },
    scripts=["pypm2-cli"],
    include_package_data=True,
    zip_safe=False,
)
