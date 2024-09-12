import os
import hashlib
import pathlib
import typing

from serial.tools import list_ports

from ._protobuf import Protobuf
from . import protobuf as pb


def resolve_port(portname: str = 'auto') -> str | None:
    if portname != 'auto':
        return portname
    
    ports = list_ports.grep('flip_')
    flippers = list(ports)

    if len(flippers) == 1:
        flipper = flippers[0]
        
        return flipper.device
    
    return None


def upload_file(
    protobuf: Protobuf,
    source: str,
    target: str,
    chunk_size: int = 1024,
    on_progress: typing.Callable[[int, int], None] = None
) -> None:
    if not os.path.isfile(source):
        raise Exception('source file not found')

    request = pb.storage_pb2.Md5sumRequest()
    request.path = target

    response = protobuf.send_and_read_answer(request, 'storage_md5sum_request')

    target_digest: str = response.storage_md5sum_response.md5sum if response.command_status == 0 else ''

    source_size = os.path.getsize(source)

    with open(source, 'rb') as fp:
        source_digest = hashlib.file_digest(fp, 'md5').hexdigest()

        if source_digest == target_digest:
            return

        fp.seek(0, os.SEEK_SET)

        request = pb.storage_pb2.WriteRequest()
        request.path = target

        seq = protobuf.get_next_seq()

        for chunk_start in range(0, source_size, chunk_size):
            request.file.data = fp.read(chunk_size)

            chunk_end = chunk_start + len(request.file.data)

            has_next = chunk_start + chunk_size < source_size
            
            if on_progress:
                on_progress(chunk_end, source_size)

            protobuf.send(request, 'storage_write_request', has_next, seq)
        
        response = protobuf.read_answer()

        if response.command_status != 0:
            raise Exception('file upload failed')
