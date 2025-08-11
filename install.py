#!/usr/bin/env python3
"""Setup script para o Sistema de Backup."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sistema-backup",
    version="2.1.0",
    author="Equipe Backup",
    author_email="backup@exemplo.com",
    description="Sistema completo de backup com sincronização cloud",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/usuario/sistema-backup",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Archiving :: Backup",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=1.0",
        ],
        "gui": [
            "tkinter",
            "pyqt5",
        ],
    },
    entry_points={
        "console_scripts": [
            "backup-cli=backup_system.cli:main",
            "backup-gui=backup_system.gui:main",
            "backup-web=backup_system.web:main",
        ],
    },
    include_package_data=True,
    package_data={
        "backup_system": [
            "templates/*.html",
            "static/*.css",
            "static/*.js",
        ],
    },
)
