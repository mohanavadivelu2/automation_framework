import os
from typing import List, Dict, Any
from global_config.project_configuration import TEST_CASE_COMMON_COMMAND
from .test_case_helper import load_json
from logger import LogManager


def expand_common_commands(commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Recursively expand common commands in a list of commands.
    
    This function processes a list of command dictionaries and expands any that
    contain a 'common_command' key by loading the referenced common command file
    and recursively expanding its commands.
    
    Args:
        commands: List of command dictionaries to process
        
    Returns:
        List of expanded command dictionaries with all common commands resolved
    """
    expanded_commands = []
    alog = LogManager.get_instance().get_application_logger()
    
    for command in commands:
        if "common_command" in command:
            common_command_file = os.path.join(TEST_CASE_COMMON_COMMAND, command["common_command"])
            common_data = load_json(common_command_file)

            if common_data and "command" in common_data:
                alog.i(f"Expanding File >>> {command['common_command']}")
                nested_commands = expand_common_commands(common_data["command"])
                expanded_commands.extend(nested_commands)
            else:
                alog.w(f"Invalid or missing common command file: {common_command_file}")
        else:
            expanded_commands.append(command)

    return expanded_commands
