from google.protobuf.json_format import MessageToDict

from fssdk import resolve_port, CLI, Protobuf, protobuf as pb

port = resolve_port()

cli = CLI(port)

cli.write_command('start_rpc_session')

protobuf = Protobuf(cli)

request = pb.storage_pb2.ListRequest()
request.path = '/ext'

response: pb.flipper_pb2.Main = protobuf.send_and_read_answer(request, 'storage_list_request')

for file in response.storage_list_response.file:
    print(file)

while response.has_next:
    response = protobuf.read_answer()
    
    for file in response.storage_list_response.file:
        print(file)
