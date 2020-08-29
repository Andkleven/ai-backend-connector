"""
Usage: robot_udp_driver.py [options] LEFT RIGHT

Options:
    --help  This help.
    --address ADDRESS  Address to connect. [default: 192.168.1.199]
    --port PORT        Port to use. [default: 50052]
"""

import proto.RobotSystemCommunication_pb2 as rsc_pb2
import socket
import docopt


UDP_IP = "192.168.1.199"
UDP_PORT = 50052



if __name__ == "__main__":
    opts = docopt.docopt(__doc__)

    motor_values = rsc_pb2.RobotActionRequest(
        leftMotorAction=int(opts['LEFT'].replace('~', '-')),
        rightMotorAction=int(opts['RIGHT'].replace('~', '-')))
    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock.sendto(motor_values.SerializeToString(), (opts['--address'], int(opts['--port'])))
    print("bar")
