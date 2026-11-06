"""Opt-in, source-bound CAD/CAE comparison; never a railway release authority."""
from .cases import FLAGS, identity

PROVIDERS = {
    'freecad': dict(role='CAD reference', status='retained', eligible='existing native CAD contracts'),
    'solidcraft': dict(role='parametric CAD', status='pilot', eligible='verified primitive subsets; exact STEP comparison required'),
    'calculix': dict(role='structural reference', status='retained', eligible='existing source-bound numerical methods'),
    'fieldcraft': dict(role='mechanical analysis', status='pilot', eligible='matched linear-isotropic controls only'),
    'gmsh_getdp': dict(role='electromagnetics', status='retained', eligible='existing electromagnetic methods'),
    'ifcopenshell': dict(role='BIM exchange', status='retained', eligible='existing IFC verification'),
}
