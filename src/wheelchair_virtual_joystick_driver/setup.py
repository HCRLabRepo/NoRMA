from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup
d = generate_distutils_setup(
    packages=['wheelchair_virtual_joystick_driver'],
    package_dir={'': 'src'}
)
setup(**d)