## Generate proto codes
### gRPC code for Unity Simulation communication
```sh
python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. ./proto/RobotBackendCommunication.proto
```