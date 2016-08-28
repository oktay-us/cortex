__all__ = ['ni_dataset']

from ni_dataset import *

_classes = {}
from . import mri, fmri, snp
_modules = [mri, fmri, snp]
for module in _modules: _classes.update(**module._classes)