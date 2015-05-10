from setuptools import setup, find_packages
setup(
    name='author',
    version='1.0',
    long_description="personal blog",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=open("requirements.txt", "r").read(),
    entry_points={
        'console_scripts': ['run-server=runserver:run_server',
                            'import-posts=import:import_posts']
    }
)
