package main

import (
	"fmt"
	"log"
	"ofabel/fssdk/flipper"
)

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
	err = f0.StartRpcSession()

	if err != nil {
		log.Fatal(err)
	}

	data, err := f0.GetStorageList("/ext/test")

	if err != nil {
		log.Fatal(err)
	}

	for _, file := range data {
		println(file.Name)
	}

	f0.Close()
}
