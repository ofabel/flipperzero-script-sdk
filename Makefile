.PHONY: install
update:
	git submodule update --remote ./flipperzero-protobuf && git add ./flipperzero-protobuf

.PHONY: clean
clean:
	rm -rf ./fssdk/proto

.PHONY: protobuf
protobuf: clean
	mkdir ./fssdk/proto
	./protoc --proto_path=./flipperzero-protobuf --python_out=pyi_out:./fssdk/proto ./flipperzero-protobuf/*.proto
	sed -i 's/^import/from . import/g' ./fssdk/proto/flipper_pb2.py ./fssdk/proto/flipper_pb2.pyi
	touch ./fssdk/proto/__init__.py

.PHONY: build
build:
	source venv/bin/activate && hatch build

.PHONY: publish
publish: build
	source venv/bin/activate && hatch publish dist/*
