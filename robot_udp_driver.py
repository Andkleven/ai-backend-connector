import proto.RobotSystemCommunication_pb2 as rsc_pb2
import socket

UDP_IP = "192.168.1.142"
UDP_PORT = 50052

if __name__ == "__main__":
    motor_values = rsc_pb2.RobotActionRequest(
        leftMotorAction=200,
        rightMotorAction=-400)
    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock.sendto(motor_values.SerializeToString(), (UDP_IP, UDP_PORT))