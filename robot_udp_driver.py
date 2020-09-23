"""
Usage: robot_udp_driver.py [options] motor [--timeout=TIMEOUT] LEFT RIGHT
       robot_udp_driver.py [options] ping

Options:
    --help  This help.
    --address ADDRESS  Address to connect. [default: 192.168.1.199]
    --socket-timeout TIMEOUT
                       Wait for robot reply for TIMEOUT seconds. [default: 2]
    --port PORT        Port to use. [default: 50052]
    --timeout=TIMEOUT  Timeout for motor command in milliseconds.
                       [default: 200]
    --broadcast        Broadcast the request.
"""
import sys
import os.path
sys.path.append(os.path.dirname(__file__))
import proto.RobotSystemCommunication_pb2 as rsc_pb2
import socket
import docopt


UDP_IP = "192.168.1.199"
UDP_PORT = 50052


if __name__ == "__main__":
    opts = docopt.docopt(__doc__)

    if opts['motor']:
        request = rsc_pb2.RobotRequest(
            reqId=1,
            act=rsc_pb2.RobotActionRequest(
                        leftMotorAction=int(opts['LEFT'].replace('~', '-')),
                        rightMotorAction=int(opts['RIGHT'].replace('~', '-')),
                        actionTimeout=int(opts['--timeout'])))
    elif opts['ping']:
        request = rsc_pb2.RobotRequest(
            reqId=1,
            ping=rsc_pb2.RobotPingRequest())
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 0))
    if opts['--broadcast']:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(request.SerializeToString(), (opts['--address'], int(opts['--port'])))
    sock.settimeout(int(opts['--socket-timeout']))
    try:
        data, from_addr = sock.recvfrom(100)
        reply = rsc_pb2.RobotResponse()
        reply.ParseFromString(data)
        print(f"{from_addr[0]}#{from_addr[1]}:\n{reply}")
    except socket.timeout as e:
        print("no reply")
