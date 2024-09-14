.PHONY: install
update:
	git submodule update --remote ./flipperzero-protobuf && git add ./flipperzero-protobuf

.PHONY: clean
clean:
	rm -rf ./dist
	rm -rf ./fssdk/proto
	mkdir -p ./dist

.PHONY: format
format:
	gofmt -w .

.PHONY: run
run:
	go run .

.PHONY: build
build: clean
	go build -o ./dist .

.PHONY: protobuf
protobuf: clean
	mkdir ./fssdk/proto
	./protoc --proto_path=./flipperzero-protobuf --python_out=pyi_out:./fssdk/proto ./flipperzero-protobuf/*.proto
	sed -i 's/^import/from . import/g' ./fssdk/proto/flipper_pb2.py ./fssdk/proto/flipper_pb2.pyi
