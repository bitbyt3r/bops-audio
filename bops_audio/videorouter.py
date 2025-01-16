import socketserver
import threading
import socket
import random
import queue
import time

class VideohubSimulator(socketserver.StreamRequestHandler):
    spacer = "\n"
    num_inputs = 8
    num_outputs = 8
    
    def send_block(self, header, values=None):
        if not values:
            return
        self.wfile.write(f"{header}:{self.spacer}".encode('UTF-8'))
        self.wfile.write(self.spacer.join(values).encode('UTF-8'))
        self.wfile.write(self.spacer.encode('UTF-8'))
        self.wfile.write(self.spacer.encode('UTF-8'))
        
    def handle(self):
        print("Client connected")
        self.send_block("PROTOCOL PREAMBLE", ["Version: 2.3"])
        self.send_block("VIDEOHUB DEVICE", [
            "Device present: true",
            "Model name: Blackmagic Smart Videohub",
            f"Video inputs: {self.num_inputs}",
            "Video processing units: 0",
            f"Video outputs: {self.num_outputs}",
            "Video monitoring outputs: 0",
            "Serial ports: 0"
        ])
        self.send_block("INPUT LABELS", [f"{x} CH {x}" for x in range(self.num_inputs)])
        self.send_block("OUTPUT LABELS", [f"{x} Output {x}" for x in range(self.num_outputs)])
        self.send_block("VIDEO OUTPUT ROUTING", [f"{x} {random.choice(list(range(self.num_inputs)))}" for x in range(self.num_outputs)])
        self.send_block("VIDEO OUTPUT LOCKS", [f"{x} {random.choice(['U', 'L', 'O'])}" for x in range(self.num_outputs)])
        #while True:
        #    self.send_block("VIDEO OUTPUT ROUTING", ["0 0", "1 1", "2 2", "3 3", "4 4", "5 5", "6 6", "7 7"])
        #    time.sleep(5)
        #    self.send_block("VIDEO OUTPUT ROUTING", ["0 0", "1 0", "2 0", "3 0", "4 0", "5 0", "6 0", "7 0"])
        #    time.sleep(5)
        while True:
            time.sleep(random.random())
            operation = random.choice(["VIDEO OUTPUT ROUTING", "INPUT LABELS", "OUTPUT LABELS", "VIDEO OUTPUT LOCKS"])
            quantity = random.randrange(5)
            values = []
            if operation == "VIDEO OUTPUT ROUTING":
                print("Pushing video route change")
                quantity = min(quantity, self.num_outputs)
                values = [f"{x} {random.choice(list(range(self.num_inputs)))}" for x in random.sample(list(range(self.num_outputs)), k=quantity)]
            elif operation == "INPUT LABELS":
                print("Pushing input label change")
                quantity = min(quantity, self.num_inputs)
                values = [f"{x} {random.choice(['Gamecube', 'Wii', 'PS4', 'PS5', 'XBox', 'PC', 'Bars'])}" for x in random.sample(list(range(self.num_inputs)), k=quantity)]
            elif operation == "OUTPUT LABELS":
                quantity = min(quantity, self.num_outputs)
                values = [f"{x} {random.choice(['Gamecube', 'Wii', 'PS4', 'PS5', 'XBox', 'PC', 'Bars'])}" for x in random.sample(list(range(self.num_outputs)), k=quantity)]
            elif operation == "VIDEO OUTPUT LOCKS":
                quantity = min(quantity, self.num_outputs)
                values = [f"{x} {random.choice(['U', 'O', 'L'])}" for x in random.sample(list(range(self.num_outputs)), k=quantity)]
            self.send_block(operation, values)


class DaemonServer(socketserver.ThreadingTCPServer):
    reuse_address = True
    daemon_threads = True
    block_on_close = False

def emulator():
    with DaemonServer(("0.0.0.0", 9990), VideohubSimulator) as server:
        server.serve_forever()
        
class VideoHub():
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.listen)
    
    def process(self, chunk):
        lines = chunk.split("\n")
        operation = lines[0]
        print(f"GOT OP: {operation}")
        if operation == "VIDEO OUTPUT ROUTING:":
            for line in lines[1:]:
                output, input = line.strip().split(" ")
                self.queue.put(("VIDEO OUTPUT ROUTING", int(output), int(input)))
        elif operation == "INPUT LABELS:":
            print("Got input label change", lines)
            for line in lines[1:]:
                input, label = line.strip().split(" ", 1)
                self.queue.put(("INPUT LABELS", int(input), label))
        elif operation == "OUTPUT LABELS:":
            for line in lines[1:]:
                output, label = line.strip().split(" ", 1)
                self.queue.put(("OUTPUT LABELS", int(output), label))
        elif operation == "VIDEO OUTPUT LOCKS:":
            for line in lines[1:]:
                output, lock = line.strip().split(" ", 1)
                self.queue.put(("VIDEO OUTPUT LOCKS", int(output), lock))
    
    def listen(self):
        print(f"Connecting to {self.address}:{self.port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.address, self.port))
        buffer = bytes()
        while True:
            try:
                buffer += sock.recv(1)
                buffer.replace("\r".encode('UTF-8'), "\n".encode('UTF-8'))
                sep = buffer.index("\n\n".encode('UTF-8'))
                chunk = buffer[:sep].decode('UTF-8')
                buffer = buffer[sep+2:]
                self.process(chunk)
            except ValueError:
                pass
            
    def start(self):
        self.thread.start()