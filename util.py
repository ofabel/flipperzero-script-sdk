from fssdk import resolve_port, upload_file, CLI, Protobuf, protobuf as pb

port = resolve_port()

cli = CLI(port)

cli.write_command('start_rpc_session')

protobuf = Protobuf(cli)

def progress(current, total):
    print(f'{int(100 * (current / total))}%', end='\r')

upload_file(protobuf, __file__, '/ext/test.txt', on_progress=progress)
