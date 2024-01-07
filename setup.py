from setuptools import setup


with open("ratelimiter/__init__.py") as f:
    info = {}
    for line in f:
        if line.startswith("version"):
            exec(line, info)
            break

setup(
    name="ratelimiter",
    version=info["version"],
    packages=["ratelimiter"],
    url="https://example.com",
    license="",
    author="",
    author_email="",
    description="Rate limiter",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'redis~=5.0.1'
    ]
)