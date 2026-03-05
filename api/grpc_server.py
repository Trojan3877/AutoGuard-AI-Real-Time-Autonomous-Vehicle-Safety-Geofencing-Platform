import grpc
from concurrent import futures
import inference_pb2
import inference_pb2_grpc

class InferenceService(inference_pb2_grpc.InferenceServiceServicer):
    def Predict(self, request, context):
        return inference_pb2.PredictionResponse(
            status="SAFE",
            confidence=0.92
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inference_pb2_grpc.add_InferenceServiceServicer_to_server(
        InferenceService(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()
