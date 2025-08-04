from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Get the base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Find all packages under src/
packages = find_packages(where='src')

# Add the package_dir to ensure proper imports
package_dir = {
    'motorsport_calendar': 'src/motorsport_calendar',
    'sources': 'sources',
    '': 'src',  # For any other packages under src/
}

# Include the sources package if it exists
if os.path.exists('sources'):
    packages.extend(find_packages(where='sources'))

setup(
    name="motorsport-calendar",
    version="0.1.0",
    packages=packages,
    package_dir=package_dir,
    install_requires=requirements,
    python_requires='>=3.8',
    include_package_data=True,
    zip_safe=False,
    
    # Metadata
    author="Daniel Mirrha",
    author_email="dmirrha@gmail.com",
    description="A calendar application for motorsport events",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    
    # Entry points (if any)
    entry_points={
        'console_scripts': [
            'motorsport-calendar=motorsport_calendar:main',
        ],
    },
)
