"""Backup"""

from usingversion import getattr_with_version

__getattr__ = getattr_with_version("census_backup", __file__, __name__)
