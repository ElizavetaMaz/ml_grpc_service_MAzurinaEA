import grpc
import model_pb2
import model_pb2_grpc

def run_health(channel):
    stub = model_pb2_grpc.PredictionServiceStub(channel)
    resp = stub.Health(model_pb2.HealthRequest(), timeout=3.0)
    print({"status": resp.status, "model_version": resp.model_version})

def run_predict(channel):
    stub = model_pb2_grpc.PredictionServiceStub(channel)

    # пример: Wine‑датасет, часть признаков
    # пример: Wine‑датасет, все 13 признаков
    req = model_pb2.PredictRequest(
        alcohol=14.5,
        malic_acid=2.1,
        ash=2.3,
        alcalinity_of_ash=15.0,
        magnesium=106.0,
        total_phenols=2.8,
        flavanoids=3.0,
        nonflavanoid_phenols=0.3,
        proanthocyanins=1.9,
        color_intensity=5.6,
        hue=1.04,
        od280_od315=3.92,
        proline=1200.0,
    )

    resp = stub.Predict(req, timeout=3.0)
    print({
        "prediction": resp.prediction,
        "confidence": resp.confidence,
    })

if __name__ == "__main__":
    with grpc.insecure_channel("localhost:50051") as channel:
        run_health(channel)
        run_predict(channel)