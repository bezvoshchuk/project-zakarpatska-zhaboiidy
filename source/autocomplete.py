from __future__ import annotations

from prompt_toolkit.styles import Style


def get_autocomplete(list_of_names: list[str], supported_commands: list[str]) -> dict[str, list[str] | None]:
    result = {}

    commands_with_names = [
        'add-birthday', 'add-address', 'add-email', 'update-phone', 'phone', 'show-birthday', 'delete-contact',
        'delete-email', 'delete-phone', 'delete-address', 'delete-birthday', 'update-email', 'update-address',
        'update-birthday'
    ]

    names = {}
    for name in list_of_names or []:
        names[name] = None

    for command in supported_commands:
        result[command] = names if command in commands_with_names else None

    return result


style = Style.from_dict({
    'completion-menu.completion': 'bg:#008888 #ffffff',
    'completion-menu.completion.current': 'bg:#00aaaa #000000',
    'scrollbar.background': 'bg:#88aaaa',
    'scrollbar.button': 'bg:#222222',
})
