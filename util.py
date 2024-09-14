from fssdk import resolve_port, CLI, Protobuf, Flipper

port = resolve_port()

cli = CLI(port)

cli.write_command('start_rpc_session')

protobuf = Protobuf(cli)
flipper = Flipper(protobuf)

def progress(current, total):
    print(f'{int(100 * (current / total))}%', end='\r')

flipper.upload_file(__file__, '/ext/test/test/teste.txt', on_progress=progress)

for item in flipper.get_list('/ext'):
    print(item.path)
