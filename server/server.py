import grpc, os
import numpy as np
from concurrent import futures
import model_pb2, model_pb2_grpc
from server.model_predict import ModelRunner

MODEL_PATH = os.getenv("MODEL_PATH", "models/model.pkl")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0.0")
PORT = int(os.getenv("PORT", "50051"))

class PredictionService(model_pb2_grpc.PredictionServiceServicer):
    def __init__(self):
        try:
            self.runner = ModelRunner(MODEL_PATH, version=MODEL_VERSION)
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            self.runner = None

    def Health(self, request, context):
        if self.runner is None:
            return model_pb2.HealthResponse(status="error", model_version=MODEL_VERSION) # если модели нет то должен выдавать ошибку (реализовано, чтобы разные ответы можно было получить в рамках ДЗ2)
        return model_pb2.HealthResponse(status="ok", model_version=self.runner.version)


    def Predict(self, request, context):
        if self.runner is None:
            context.set_details("Model not loaded")
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            return model_pb2.PredictResponse()

        try:
            # собираем все 13 признаков в правильном порядке
            ordered_values = [
                request.alcohol,
                request.malic_acid,
                request.ash,
                request.alcalinity_of_ash,
                request.magnesium,
                request.total_phenols,
                request.flavanoids,
                request.nonflavanoid_phenols,
                request.proanthocyanins,
                request.color_intensity,
                request.hue,
                request.od280_od315,
                request.proline,
            ]
            X = np.array(ordered_values).reshape(1,-1)

            pred, conf = self.runner.predict(X)
            return model_pb2.PredictResponse(
                prediction=str(pred),
                confidence=float(conf)
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"internal error: {e}")
            return model_pb2.PredictResponse()

def serve():
    options = [
        ("grpc.max_send_message_length", 50 * 1024 * 1024),
        ("grpc.max_receive_message_length", 50 * 1024 * 1024),
    ]
    server = grpc.server(futures.ThreadPoolExecutor(), options=options)
    model_pb2_grpc.add_PredictionServiceServicer_to_server(PredictionService(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    print(f"gRPC server started on :{PORT}, model={MODEL_PATH}, version={MODEL_VERSION}")
    server.wait_for_termination()

if __name__ == "__main__":
    try:
        import uvloop
        uvloop.install()
    except Exception:
        pass
    serve()