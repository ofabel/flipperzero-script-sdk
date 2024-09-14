import os
import hashlib
import pathlib
import typing

from serial.tools import list_ports


def resolve_port(portname: str = 'auto') -> str | None:
    if portname != 'auto':
        return portname
    
    ports = list_ports.grep('flip_')
    flippers = list(ports)

    if len(flippers) == 1:
        flipper = flippers[0]
        
        return flipper.device
    
    return None
