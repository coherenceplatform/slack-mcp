#!/usr/bin/env python3
"""Setup configuration for Slack MCP Server."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='slack-mcp-server',
    version='0.1.0',
    author='Zachary Zaro',
    author_email='oss@withcoherence.com',
    description='A Model Context Protocol server for Slack integration',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/coherenceplatform/slack-mcp-server',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Framework :: AsyncIO',
    ],
    keywords='slack mcp model-context-protocol ai assistant integration',
    packages=find_packages(exclude=['tests*', 'docs*']),
    py_modules=['main'],
    python_requires='>=3.9',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'ruff>=0.1.0',
            'mypy>=1.0.0',
            'types-httpx',
        ],
    },
    entry_points={
        'console_scripts': [
            'slack-mcp-server=main:run',
        ],
        'mcp.servers': [
            'slack=main:run',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/coherenceplatform/slack-mcp-server/issues',
        'Source': 'https://github.com/coherenceplatform/slack-mcp-server',
        'Documentation': 'https://github.com/coherenceplatform/slack-mcp-server#readme',
    },
    include_package_data=True,
    zip_safe=False,
)