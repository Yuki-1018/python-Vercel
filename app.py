from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit, disconnect
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

def countdown(room):
    for i in range(5, 0, -1):
        socketio.emit('countdown', {'count': i}, room=room)
        time.sleep(1)
    socketio.emit('start_game', room=room)

@socketio.on('create_room')
def on_create(data):
    room = data['room']
    if room not in rooms:
        join_room(room)
        rooms[room] = {'players': [request.sid], 'status': 'waiting'}
        emit('room_created', {'room': room})
    else:
        emit('room_exists', {'room': room})

@socketio.on('join_room')
def on_join(data):
    room = data['room']
    if room in rooms and len(rooms[room]['players']) < 2:
        join_room(room)
        rooms[room]['players'].append(request.sid)
        if len(rooms[room]['players']) == 2:
            rooms[room]['status'] = 'countdown'
            threading.Thread(target=countdown, args=(room,)).start()
        emit('room_joined', {'room': room})
    elif room in rooms and len(rooms[room]['players']) >= 2:
        emit('room_full', {'room': room})
    else:
        emit('room_not_found', {'room': room})

@socketio.on('update')
def on_update(data):
    room = data['room']
    emit('update', data, room=room, include_self=False)

@socketio.on('game_over')
def on_game_over(data):
    room = data['room']
    emit('game_over', room=room)
    rooms[room]['status'] = 'waiting'
    rooms[room]['players'] = []

@socketio.on('disconnect')
def on_disconnect():
    for room, info in rooms.items():
        if request.sid in info['players']:
            info['players'].remove(request.sid)
            if len(info['players']) == 0:
                del rooms[room]
            else:
                emit('opponent_disconnected', room=room)
                info['status'] = 'waiting'
                leave_room(room)
            break

if __name__ == '__main__':
    socketio.run(app, debug=True)
