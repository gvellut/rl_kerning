from setuptools import find_packages, setup

with open("rl_kerning/__init__.py") as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            break

with open("README.md") as f:
    readme = f.read()

with open("requirements.txt") as f:
    requirements = f.readlines()

with open("requirements-dev.txt") as f:
    requirements_dev = f.readlines()

setup_args = dict(
    name="rl_kerning",
    version=version,
    description="HarfBuzz kerning / ligatures for Reportlab",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/gvellut/rl_kerning",
    author="Guilhem Vellut",
    author_email="g@vellut.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Printing",
    ],
    keywords="reportlab pdf publishing book",
    packages=find_packages(exclude=["docs", "tests"]),
    install_requires=requirements,
    extras_require={"dev": requirements_dev},
    project_urls={
        "Bug Reports": "https://github.com/gvellut/rl_kerning/issues",
        "Source": "https://github.com/gvellut/rl_kerning",
    },
)

setup(**setup_args)
