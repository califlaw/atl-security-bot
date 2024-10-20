from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def _split_buttons(buttons, n_cols: int = 1) -> List:
    return [buttons[i : i + n_cols] for i in range(0, len(buttons), n_cols)]


def build_menu(
    buttons: List[InlineKeyboardButton],
    n_cols: int,
    header_buttons: List[InlineKeyboardButton]
    | InlineKeyboardButton
    | None = None,
    footer_buttons: List[InlineKeyboardButton]
    | InlineKeyboardButton
    | None = None,
) -> List[List[InlineKeyboardButton]]:
    menu = _split_buttons(buttons, n_cols)
    if header_buttons:
        menu.insert(
            0,
            header_buttons
            if isinstance(header_buttons, list)
            else [header_buttons],
        )
    if footer_buttons:
        menu.append(
            footer_buttons
            if isinstance(footer_buttons, list)
            else [footer_buttons]
        )
    return menu


def make_reply_markup(
    button_list: List[InlineKeyboardButton],
    colls: int = 1,
    header_buttons: List[InlineKeyboardButton]
    | InlineKeyboardButton
    | None = None,
    footer_buttons: List[InlineKeyboardButton]
    | InlineKeyboardButton
    | None = None,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        build_menu(
            button_list,
            n_cols=colls,
            header_buttons=header_buttons,
            footer_buttons=footer_buttons,
        )
    )
