package flipper

import (
	"errors"
	"strings"

	"github.com/albenik/go-serial/v2"
	"github.com/albenik/go-serial/v2/enumerator"
)

var ErrNoFlipperFound = errors.New("no flipper device found")
var ErrNoTerminalFound = errors.New("no terminal found")
var ErrCommandNotSend = errors.New("unable to send command")

func GetFlipperPort() (string, error) {
	ports, err := enumerator.GetDetailedPortsList()

	if err != nil {
		return "", err
	}
	if len(ports) == 0 {
		return "", ErrNoFlipperFound
	}
	for _, port := range ports {
		if strings.HasPrefix(port.SerialNumber, "flip_") {
			return port.Name, nil
		}
	}

	return "", ErrNoFlipperFound
}

type Flipper struct {
	port *serial.Port
}

var TerminalDelimiter = []byte("\n>: ")

func Open(port string) (*Flipper, error) {
	handle, err := serial.Open(port,
		serial.WithBaudrate(230400),
		serial.WithDataBits(8),
		serial.WithParity(serial.NoParity),
		serial.WithStopBits(serial.OneStopBit),
		serial.WithReadTimeout(1000),
		serial.WithWriteTimeout(1000),
		serial.WithHUPCL(true))

	if err != nil {
		return nil, err
	}

	return &Flipper{
		port: handle,
	}, nil
}

func (f0 *Flipper) Close() error {
	return f0.port.Close()
}

func (f0 *Flipper) ReadUntilTerminal() ([]byte, error) {
	data, found, err := f0.ReadUntil(TerminalDelimiter)

	if err != nil {
		return nil, err
	}

	if !found {
		return nil, ErrNoTerminalFound
	}

	return data, nil
}

func (f0 *Flipper) ReadUntil(needle []byte) ([]byte, bool, error) {
	character := make([]byte, 1)
	buffer := make([]byte, 1)
	i := 0

	for {
		if i == len(needle) {
			return buffer[1:], true, nil
		}

		n, err := f0.port.Read(character)

		if err != nil {
			return nil, false, err
		}

		if n == 0 {
			return buffer[1:], false, nil
		}

		if character[0] == needle[i] {
			i++
		} else {
			i = 0
		}

		buffer = append(buffer, character...)
	}
}

func (f0 *Flipper) ReadLine() ([]byte, error) {
	character := make([]byte, 1)
	buffer := make([]byte, 1)
	cr := false

	for {
		n, err := f0.port.Read(character)

		if err != nil {
			return nil, err
		}

		if n == 0 {
			return buffer[1:], nil
		}

		if character[0] == '\r' {
			cr = true

			continue
		}

		if cr && character[0] == '\n' {
			return buffer[1:], nil
		}

		cr = false

		buffer = append(buffer, character...)
	}
}

func (f0 *Flipper) SendCommand(command string) error {
	raw_command := []byte(command + "\r")

	n, err := f0.port.Write(raw_command)

	if err != nil {
		return err
	}

	if n != len(raw_command) {
		return ErrCommandNotSend
	}

	return nil
}
