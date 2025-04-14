from setuptools import setup, find_packages

setup(
    name="p2pchat",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "p2pchat-server=p2pchat.server:start_server",
            "p2pchat-client=p2pchat.client:start_client"
        ]
    },
    author="Trieu Tran",
    description="Peer-to-peer terminal chat app using sockets and SQLite.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
)
