from setuptools import setup, find_packages

setup(
    name="uipath-reframework-generator",
    version="1.0.0",
    description="Generate UiPath ReFramework projects from Process Definition Documents using Claude AI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="ReFramework Generator Contributors",
    url="https://github.com/alessiodonato/uipath-reframework-generator",
    license="MIT",
    packages=find_packages(),
    package_data={
        "": [
            "assets/xaml-templates/*.xaml",
            "references/*.md",
        ]
    },
    install_requires=[
        "pdfminer.six>=20221105",
        "python-docx>=1.1.0",
        "openpyxl>=3.1.0",
        "anthropic>=0.25.0",
    ],
    entry_points={
        "console_scripts": [
            "reframework-gen=scripts.generate_reframework:main",
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
