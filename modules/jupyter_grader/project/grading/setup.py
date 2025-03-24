# -*- coding: utf-8 -*-
from .utils import banner


def check_dependencies():
    try:
        from colorama import Fore, Back, Style
    except Exception:
        raise Exception("libreria colorama no esta instalada")

    try:
        from emoji import emojize
    except Exception:
        raise Exception("libreria emoji no esta instalada")


def check_setup():
    check_dependencies()
    from colorama import Fore

    banner(
        Fore.GREEN
        + "Si ve este mensaje, su ambiente esta correctamente configurado :robot: :rocket:"
    )
