FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install -r requirements.txt

ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV PYTHONPATH=/app

CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
