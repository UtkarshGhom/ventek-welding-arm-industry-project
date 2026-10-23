from setuptools import find_packages, setup
import os
from glob import glob

package_name = "ventek_autonomous_welding"

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(path, filename))
    return paths

extra_files = []
for d in ["urdf", "simulation", "config", "data", "launch", "docs", "integration"]:
    for f in package_files(d):
        target_dir = os.path.join("share", package_name, os.path.dirname(f))
        extra_files.append((target_dir, [f]))

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["tests*"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml", "model.config"]),
    ] + extra_files,
    install_requires=["setuptools", "jsonschema"],
    zip_safe=True,
    maintainer="Utkarsh",
    maintainer_email="utkarsh@ventek.com",
    description="VENTEK Autonomous Welding Robotic Cell Simulation and Planning Pipeline",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "verify_cell_setup = scripts.verify_cell_setup:main",
            "view_depth_feed = scripts.view_depth_feed:main",
            "joint_state_to_gz = scripts.joint_state_to_gz:main",
            "run_pipeline = scripts.run_integration_pipeline:main",
        ],
    },
)
