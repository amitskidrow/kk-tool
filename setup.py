from setuptools import setup, find_packages

setup(
    name="secret-browser",
    version="1.0.0",
    description="A CLI tool to browse and manage secrets in GNOME Keyring",
    long_description=open("README.md").read() if open("README.md").read() else "A CLI tool to browse and manage secrets in GNOME Keyring",
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/secret-browser",
    packages=find_packages(),
    install_requires=[
        "secretstorage>=3.3.0",
    ],
    entry_points={
        "console_scripts": [
            "secret-browser=secret_browser_package.secret_browser:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.7",
)