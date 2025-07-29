"""
Handler module for UI automation commands.

This module provides handler classes for different widget types.
"""

from .base import BaseHandler
from .button import ButtonHandler
from .text import TextHandler
from .scroll import ScrollHandler
from .radio_button import RadioButtonHandler
from .mac_drop_down_button import MacDropDownButtonHandler
from .screenshot import ScreenshotHandler
from .single_template import SingleTemplateHandler
from .multi_template import MultiTemplateHandler
from .text_search import TextSearchHandler
from .image_click import ImageClickHandler
from .ios_scroll import ScrollIosHandler
from .page_source import PageSourceHandler
from .facet_page_source_search import FacetPageSourceSearchHandler
from .usb_controller import USBControllerHandler
from .adb_commands import (
    ADBHandler,
    ADBLaunchHandler,
    ADBShellHandler,
    ADBInstallHandler,
    ADBSwipeHandler,
    ADBSwipeXYHandler,
    ActivateAppHandler,
    TerminateAppHandler
)

__all__ = [
    'BaseHandler',
    'ButtonHandler',
    'TextHandler',
    'ScrollHandler',
    'RadioButtonHandler',
    'MacDropDownButtonHandler',
    'ScreenshotHandler',
    'SingleTemplateHandler',
    'MultiTemplateHandler',
    'TextSearchHandler',
    'ImageClickHandler',
    'ScrollIosHandler',
    'PageSourceHandler',
    'FacetPageSourceSearchHandler',
    'USBControllerHandler',
    'ADBHandler',
    'ADBLaunchHandler',
    'ADBShellHandler',
    'ADBInstallHandler',
    'ADBSwipeHandler',
    'ADBSwipeXYHandler',
    'ActivateAppHandler',
    'TerminateAppHandler'
]
