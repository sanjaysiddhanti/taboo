import socketio

sio = socketio.Client()

sio.connect('http://flask:5000')

@sio.event
def message(data):
    print(f'I received a message! {data}')

@sio.on('hello world')
def starting(data):
    print(data['msg'])

@sio.on('game created')
def starting(data):
    print('Created a game')
    print(data)

sio.emit('hello world')

sio.emit('create game', {'username': 'luigi'})