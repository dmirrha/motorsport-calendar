from setuptools import setup, find_packages

# This is a minimal setup.py that uses pyproject.toml for configuration
# Most of the configuration is now in pyproject.toml

if __name__ == "__main__":
    setup(
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        include_package_data=True,
    )
