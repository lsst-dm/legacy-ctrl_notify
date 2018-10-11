"""Sphinx configuration file for an LSST stack package.

This configuration only affects single-package Sphinx documentation builds.
"""

from documenteer.sphinxconfig.stackconf import build_package_configs
import lsst.ctrl.notify


_g = globals()
_g.update(build_package_configs(
    project_name='ctrl_notify',
    version=lsst.ctrl.notify.version.__version__))
