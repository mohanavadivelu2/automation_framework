from command_handler.widget.handler.button import ButtonHandler
from command_handler.widget.handler.scroll import ScrollHandler
from command_handler.widget.handler.text import TextHandler
from command_handler.widget.handler.radio_button import RadioButtonHandler
from command_handler.widget.handler.mac_drop_down_button import MacDropDownButtonHandler
from command_handler.widget.handler.screenshot import ScreenshotHandler
from command_handler.widget.handler.single_template import SingleTemplateHandler
from command_handler.widget.handler.multi_template import MultiTemplateHandler
from command_handler.widget.handler.text_search import TextSearchHandler
from command_handler.widget.handler.image_click import ImageClickHandler
from command_handler.widget.handler.ios_scroll import ScrollIosHandler
from command_handler.widget.handler.page_source import PageSourceHandler
from command_handler.widget.handler.facet_page_source_search import FacetPageSourceSearchHandler
# Import all ADB-related handlers from the consolidated adb_commands.py
from command_handler.widget.handler.adb_commands import (
    ADBHandler,
    ADBSwipeHandler,
    ADBInstallHandler,
    ADBLaunchHandler,
    ADBShellHandler,
    ADBSwipeXYHandler,
    ActivateAppHandler,
    TerminateAppHandler
)

class WidgetFactory:
    _handlers = {
        "button": ButtonHandler,
        "text": TextHandler,
        "scroll": ScrollHandler,
        "radio_button": RadioButtonHandler,
        "mac_popup_button": MacDropDownButtonHandler,
        "screenshot" : ScreenshotHandler,
        "single_template": SingleTemplateHandler,
        "multi_template": MultiTemplateHandler,
        "text_search": TextSearchHandler,
        "adb": ADBHandler,
        "image_click": ImageClickHandler,
        "ios_scroll" :ScrollIosHandler,
        "page_source": PageSourceHandler,
        "facet_page_source_search": FacetPageSourceSearchHandler,
        "adb_swipe": ADBSwipeHandler,
        "adb_install": ADBInstallHandler,
        "adb_launch": ADBLaunchHandler,
        "adb_shell": ADBShellHandler,
        "terminate_app": TerminateAppHandler,
        "activate_app": ActivateAppHandler,
        "adb_swipe_xy": ADBSwipeXYHandler
    }

    @staticmethod
    def get_handler(widget_type: str):
        handler_class = WidgetFactory._handlers.get(widget_type)
        if not handler_class:
            raise ValueError(f"No handler found for widget_type: {widget_type}")
        return handler_class()
