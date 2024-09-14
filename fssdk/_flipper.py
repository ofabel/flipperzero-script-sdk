import os
import hashlib
import pathlib
import typing
import time

from . import proto
from ._protobuf import Protobuf


class FlipperException(Exception):
    pass


class FlipperStorageException(FlipperException):
    pass


class FlipperStorageExistException(FlipperStorageException):
    pass


class FlipperStorageNotExistException(FlipperStorageException):
    pass


class FlipperStorageInvalidNameException(FlipperStorageException):
    pass


class FlipperStorageFile:
    _name: str
    _dirname: str
    _path: str
    _size: int

    def __init__(self, name: str, dirname: str, size: int):
        self._name = name
        self._dirname = dirname
        self._path = f'{dirname}/{name}'
        self._size = size
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def dirname(self) -> str:
        return self._dirname
    
    @property
    def path(self) -> str:
        return self._path
    
    @property
    def size(self) -> int:
        return self._size

    def __str__(self) -> str:
        return self._path


class Flipper:
    _protobuf: Protobuf = None
    _leeway: int = None

    def __init__(self, protobuf: Protobuf):
        self._protobuf = protobuf
    
    def get_checksum(self, path: str) -> str:
        request = proto.storage_pb2.Md5sumRequest()
        request.path = path

        response = self._protobuf.send_and_read_answer(request, 'storage_md5sum_request')

        self._assert_response(response)

        return response.storage_md5sum_response.md5sum

    def get_file_size(self, path: str) -> int:
        request = proto.storage_pb2.StatRequest()
        request.path = path

        response = self._protobuf.send_and_read_answer(request, 'storage_stat_request')

        self._assert_response(response)

        return response.storage_stat_response.file.size

    def get_timestamp(self, path: str) -> int:
        if self._leeway is None:
            self._leeway = self._get_leeway()
        
        return self._get_timestamp(path) + self._leeway
    
    def create_folder(self, path: str) -> None:
        request = proto.storage_pb2.MkdirRequest()
        request.path = path

        response = self._protobuf.send_and_read_answer(request, 'storage_mkdir_request')

        self._assert_response(response)
    
    def get_list(self, path: str, recursive: bool = True) -> typing.List[FlipperStorageFile]:
        request = proto.storage_pb2.ListRequest()
        request.path = path
        
        items: typing.List[proto.storage_pb2.File] = []

        seq = self._protobuf.send(request, 'storage_list_request')

        while True:
            response = self._protobuf.read_answer(seq)
        
            self._assert_response(response)
            
            items += response.storage_list_response.file
            
            if not response.has_next:
                break

        for item in items:
            if recursive and item.type is proto.storage_pb2.File.FileType.DIR:
                yield from self.get_list(f'{path}/{item.name}')
            elif item.type is proto.storage_pb2.File.FileType.FILE:
                yield FlipperStorageFile(item.name, path, item.size)

    def upload_file(
        self,
        source: str,
        target: str,
        chunk_size: int = 1024,
        on_progress: typing.Callable[[int, int], None] = None
    ) -> None:
        if not os.path.isfile(source):
            raise Exception('source file not found')

        try:
            target_digest = self.get_checksum(target)
        except FlipperStorageNotExistException:
            target_digest = None
        source_size = os.path.getsize(source)

        with open(source, 'rb') as fp:
            source_digest = hashlib.file_digest(fp, 'md5').hexdigest()

            if source_digest == target_digest:
                return

            fp.seek(0, os.SEEK_SET)

            request = proto.storage_pb2.WriteRequest()
            request.path = target

            seq = None

            for chunk_start in range(0, source_size, chunk_size):
                request.file.data = fp.read(chunk_size)

                chunk_end = chunk_start + len(request.file.data)

                has_next = chunk_start + chunk_size < source_size
                
                if on_progress:
                    on_progress(chunk_end, source_size)

                seq = self._protobuf.send(request, 'storage_write_request', has_next, seq)
            
            response = self._protobuf.read_answer()

            self._assert_response(response)

        return None
    
    def _get_timestamp(self, path:str) -> int:
        request = proto.storage_pb2.TimestampRequest()
        request.path = path

        response = self._protobuf.send_and_read_answer(request, 'storage_timestamp_request')

        self._assert_response(response)

        return response.storage_timestamp_response.timestamp

    def _get_leeway(self) -> int:
        path = '/ext/.ee22ab04-0001-418f-80e9-4de53badf98a'

        request = proto.storage_pb2.WriteRequest()
        request.path = path
        request.file.data = b''

        now = time.time()

        response = self._protobuf.send_and_read_answer(request, 'storage_write_request')

        self._assert_response(response)

        return now - self._get_timestamp(path)
    
    def _assert_response(self, response: proto.flipper_pb2.Main) -> None:
        if response.command_status is proto.flipper_pb2.CommandStatus.OK:
            return
        
        if response.command_status is proto.flipper_pb2.CommandStatus.ERROR_STORAGE_EXIST:
            raise FlipperStorageExistException()
        
        if response.command_status is proto.flipper_pb2.CommandStatus.ERROR_STORAGE_NOT_EXIST:
            raise FlipperStorageNotExistException()
        
        if response.command_status is proto.flipper_pb2.CommandStatus.ERROR_STORAGE_INVALID_NAME:
            raise FlipperStorageInvalidNameException()
