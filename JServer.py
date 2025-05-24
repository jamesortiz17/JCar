import socket
from JMotor import JMotor
from JServo import JServo

def main():
    motor = JMotor()
    servo = JServo()
    
    HOST = ''       # Listen on all interfaces
    PORT = 9999     # Same port as the client connects to

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    print(f"[Server] Listening for connections on port {PORT}...")

    conn, addr = server.accept()
    print(f"[Server] Connected to {addr}")

    try:
        motor.set_speed(80)  # Set initial speed
        while True:
            data = conn.recv(1024)
            if not data:
                print("[Server] Client disconnected.")
                break
            cmd = data.decode('utf-8').strip().lower()
            if cmd == 'w':
                motor.forward()
            elif cmd == 's':
                motor.backward()
            elif cmd == 'x':
                motor.stop()
            elif cmd == 'a':
                servo.turn_left()
            elif cmd == 'd':
                servo.turn_right()
            else:
                print(f"[Server] Unknown command: {cmd}")
    except KeyboardInterrupt:
        print("[Server] Interrupted by user.")
    finally:
        motor.cleanup()
        servo.cleanup()
        conn.close()
        server.close()
        print("[Server] Shutdown complete.")

if __name__ == "__main__":
    main()
