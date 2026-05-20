"""Mechanical CAD templates and placeholder fixtures.

This package keeps early Build123d part templates with the rest of the
mechanical catalogue instead of the geo/design pipeline.
"""

from .fixtures import FIXTURE_BUILDERS
from .params import DEFAULT_PARAMS, TemplateParams
from .rolling_stock import (
    body_sheet_metal_kit,
    bogie_adapter,
    bolster,
    chassis_interface_assembly,
    door_leaf,
    main_frame,
    motor_cradle,
    sandwich_panel,
)

ROLLING_STOCK_TEMPLATE_BUILDERS = {
    "main-frame": main_frame,
    "sandwich-panel": sandwich_panel,
    "door-leaf": door_leaf,
    "bogie-adapter": bogie_adapter,
    "bolster": bolster,
    "motor-cradle": motor_cradle,
    "chassis-interface-assembly": chassis_interface_assembly,
    "body-sheet-metal-kit": body_sheet_metal_kit,
}

__all__ = [
    "DEFAULT_PARAMS",
    "FIXTURE_BUILDERS",
    "ROLLING_STOCK_TEMPLATE_BUILDERS",
    "TemplateParams",
    "body_sheet_metal_kit",
    "bogie_adapter",
    "bolster",
    "chassis_interface_assembly",
    "door_leaf",
    "main_frame",
    "motor_cradle",
    "sandwich_panel",
]
