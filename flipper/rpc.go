package flipper

import (
	"encoding/binary"
	"errors"
	"fmt"
	"ofabel/fssdk/flipper/rpc/flipper"
	"ofabel/fssdk/flipper/rpc/storage"

	"google.golang.org/protobuf/proto"
)

var ErrTooManyBytes = errors.New("too many bytes when decoding varint")

func (f0 *Flipper) GetStorageList(path string) ([]*storage.File, error) {
	main_request := &flipper.Main{
		CommandId:     f0.seq,
		CommandStatus: flipper.CommandStatus_OK,
		HasNext:       false,
		Content: &flipper.Main_StorageListRequest{
			StorageListRequest: &storage.ListRequest{
				Path: path,
			},
		},
	}

	f0.seq++

	raw_request, err := proto.Marshal(main_request)

	if err != nil {
		return nil, err
	}

	var size = len(raw_request)
	var raw_size = uint64(size)
	var bytes = make([]byte, 1)
	var buffer = binary.AppendUvarint(bytes, raw_size)

	buffer = append(buffer[1:], raw_request...)

	f0.port.Write(buffer)

	response, err := f0.ReadAny()

	if err != nil {
		return nil, err
	}

	if response.CommandStatus != flipper.CommandStatus_OK {
		return nil, fmt.Errorf("%s", response.CommandStatus)
	}

	return response.GetStorageListResponse().File, nil
}

func (f0 *Flipper) ReadAny() (*flipper.Main, error) {
	size, err := f0.readVariant32()

	if err != nil {
		return nil, err
	}

	raw_data := make([]byte, size)

	_, err = f0.port.Read(raw_data)

	if err != nil {
		return nil, err
	}

	data := &flipper.Main{}

	err = proto.Unmarshal(raw_data, data)

	return data, err
}

func (f0 *Flipper) readVariant32() (uint32, error) {
	const MASK = (1 << 32) - 1

	var result = uint32(0)
	var shift = uint32(0)

	var buffer = make([]byte, 1)
	var raw_data = make([]byte, 4)

	for {
		n, err := f0.port.Read(buffer)

		if err != nil {
			return 0, err
		}

		if n == 0 {
			return 0, err
		} else {
			raw_data[0] = buffer[0]
		}

		var data = binary.LittleEndian.Uint32(raw_data)

		result |= (data & 0x7F) << shift

		if data&0x80 == 0 {
			result &= MASK

			return result, nil
		}

		shift += 7

		if shift >= 64 {
			return 0, ErrTooManyBytes
		}
	}
}
