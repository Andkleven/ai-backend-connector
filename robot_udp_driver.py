"""
Usage: robot_udp_driver.py [options] motor [--timeout=TIMEOUT] LEFT RIGHT

Options:
    --help  This help.
    --address ADDRESS  Address to connect. [default: 192.168.1.199]
    --port PORT        Port to use. [default: 50052]
    --timeout=TIMEOUT  Timeout for motor command in milliseconds.
                       [default: 200]
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

    motor_values = rsc_pb2.RobotRequest(
        reqId=1,
        act=rsc_pb2.RobotActionRequest(
                    leftMotorAction=int(opts['LEFT'].replace('~', '-')),
                    rightMotorAction=int(opts['RIGHT'].replace('~', '-')),
                    actionTimeout=int(opts['--timeout'])))
    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock.sendto(motor_values.SerializeToString(), (opts['--address'], int(opts['--port'])))
