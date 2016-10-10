import os
from setuptools import setup

def find_package_data(dirname):
    def find_paths(dirname):
        items = []
        for fname in os.listdir(dirname):
            path = os.path.join(dirname, fname)
            if os.path.isdir(path):
                items += find_paths(path)
            elif not path.endswith(".py") and not path.endswith(".pyc"):
                items.append(path)
        return items
    items = find_paths(dirname)
    return [os.path.relpath(path, dirname) for path in items]

project_name = "pycbc-cal"
project_version = "0.0.dev1"
project_url = "https://github.com/cmbiwer/pycbc-cal"
project_description = "A python package for testing effects on calibration on the matched filter output of LIGO data."
project_keywords = ["ligo", "physics"]

author_name = "Christopher M. Biwer"
author_email = "cmbiwer@gmail.com"

scripts_list = [
    "bin/pycbc_adjust_strain",
    "bin/pycbc_make_cal_workflow",
]

packages_list = [
    "pycbc_cal",
]

data_dict = {
}

setup(name=project_name,
      version=project_version,
      description=project_description,
      url=project_url,
      keywords=project_keywords,
      author=author_name,
      author_email=author_email,
      scripts=scripts_list,
      packages=packages_list,
      package_data=data_dict,
      zip_safe=False,
)
