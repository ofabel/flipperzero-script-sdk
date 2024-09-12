.PHONY: install
update:
	git submodule update --remote ./flipperzero-protobuf && git add ./flipperzero-protobuf

.PHONY: clean
clean:
	rm -rf ./fssdk/protobuf

.PHONY: protobuf
protobuf: clean
	mkdir ./fssdk/protobuf
	./protoc --proto_path=./flipperzero-protobuf --python_out=pyi_out:./fssdk/protobuf ./flipperzero-protobuf/*.proto
	sed -i 's/^import/from . import/g' ./fssdk/protobuf/flipper_pb2.py ./fssdk/protobuf/flipper_pb2.pyi
	touch ./fssdk/protobuf/__init__.py

.PHONY: build
build:
	source venv/bin/activate && hatch build

.PHONY: publish
publish: build
	source venv/bin/activate && hatch publish dist/*
