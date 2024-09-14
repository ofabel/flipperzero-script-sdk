package main

import (
	"fmt"
	"ofabel/fssdk/flipper"

	"github.com/albenik/go-serial/v2"
)

func readLine(port *serial.Port) ([]byte, error) {
	character := make([]byte, 1)
	buffer := make([]byte, 1)
	cr := false

	for {
		n, err := port.Read(character)

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

func main() {
	port, err := flipper.GetFlipperPort()

	if err != nil {
		fmt.Println(err)

		return
	}

	f0, err := flipper.Open(port)

	if err != nil {
		print(err)

		return
	}

	f0.ReadUntilTerminal()
	f0.SendCommand("storage list /ext")
	data, _ := f0.ReadUntilTerminal()

	fmt.Println(string(data))

	f0.Close()
}
