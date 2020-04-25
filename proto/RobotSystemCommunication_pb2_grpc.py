# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from proto import RobotSystemCommunication_pb2 as proto_dot_RobotSystemCommunication__pb2


class RobotFrontendStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.MakeAction = channel.unary_unary(
        '/robotsystemcommunication.RobotFrontend/MakeAction',
        request_serializer=proto_dot_RobotSystemCommunication__pb2.RobotActionRequest.SerializeToString,
        response_deserializer=proto_dot_RobotSystemCommunication__pb2.RobotActionResponse.FromString,
        )


class RobotFrontendServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def MakeAction(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_RobotFrontendServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'MakeAction': grpc.unary_unary_rpc_method_handler(
          servicer.MakeAction,
          request_deserializer=proto_dot_RobotSystemCommunication__pb2.RobotActionRequest.FromString,
          response_serializer=proto_dot_RobotSystemCommunication__pb2.RobotActionResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'robotsystemcommunication.RobotFrontend', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class BrainServerStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetAction = channel.unary_unary(
        '/robotsystemcommunication.BrainServer/GetAction',
        request_serializer=proto_dot_RobotSystemCommunication__pb2.BrainActionRequest.SerializeToString,
        response_deserializer=proto_dot_RobotSystemCommunication__pb2.BrainActionResponse.FromString,
        )


class BrainServerServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def GetAction(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_BrainServerServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetAction': grpc.unary_unary_rpc_method_handler(
          servicer.GetAction,
          request_deserializer=proto_dot_RobotSystemCommunication__pb2.BrainActionRequest.FromString,
          response_serializer=proto_dot_RobotSystemCommunication__pb2.BrainActionResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'robotsystemcommunication.BrainServer', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class SimulationServerStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetScreenCapture = channel.unary_unary(
        '/robotsystemcommunication.SimulationServer/GetScreenCapture',
        request_serializer=proto_dot_RobotSystemCommunication__pb2.SimulationScreenCaptureRequest.SerializeToString,
        response_deserializer=proto_dot_RobotSystemCommunication__pb2.SimulationScreenCaptureResponse.FromString,
        )
    self.MakeAction = channel.unary_unary(
        '/robotsystemcommunication.SimulationServer/MakeAction',
        request_serializer=proto_dot_RobotSystemCommunication__pb2.SimulationActionRequest.SerializeToString,
        response_deserializer=proto_dot_RobotSystemCommunication__pb2.SimulationActionResponse.FromString,
        )


class SimulationServerServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def GetScreenCapture(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def MakeAction(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_SimulationServerServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetScreenCapture': grpc.unary_unary_rpc_method_handler(
          servicer.GetScreenCapture,
          request_deserializer=proto_dot_RobotSystemCommunication__pb2.SimulationScreenCaptureRequest.FromString,
          response_serializer=proto_dot_RobotSystemCommunication__pb2.SimulationScreenCaptureResponse.SerializeToString,
      ),
      'MakeAction': grpc.unary_unary_rpc_method_handler(
          servicer.MakeAction,
          request_deserializer=proto_dot_RobotSystemCommunication__pb2.SimulationActionRequest.FromString,
          response_serializer=proto_dot_RobotSystemCommunication__pb2.SimulationActionResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'robotsystemcommunication.SimulationServer', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
