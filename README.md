# GPU Spot Scheduler (GSS)

<p align="center">
  <a href="https://gss.readthedocs.io/en/latest/" target="_blank">
    <img src="https://readthedocs.org/projects/gss/badge/?version=latest" alt="Documentation Status" />
  </a>
  <a href="https://github.com/tsaol/GSS/releases/tag/0.1" target="_blank">
    <img src="https://img.shields.io/github/v/release/gss-org/gss" alt="GitHub release" />
  </a>
  <a href="https://github.com/tsaol/GSS/tree/main?tab=Apache-2.0-1-ov-file" target="_blank">
    <img src="https://img.shields.io/github/license/gss-org/gss" alt="License" />
  </a>
</p>

<p align="center">
  <b> LLM Inference on AWS GPU Spot Instances</b>
</p>

GSS is a framework for efficient and cost-effective deployment of large language models (LLMs) aon AWS spot GPU instances. Base on [SkyPilot](https://github.com/skypilot-org/skypilot) v0.6, GSS inherits its powerful job orchestration capabilities.

## 🚀 Features

- **Optimized LLM Inference**: Integration with popular LLM frameworks, auto-batching, and model offloading for maximum GPU utilization.
- **Cost Savings**: Leverages cheap AWS spot instances for up to 90% cost reduction compared to on-demand.
- **Simplified Deployment**: Launch inference endpoints with a single command and automatic scaling.
- **Flexible Inference Modes**: Supports both real-time and offline batch inference.

## 🛠️ Quick Start

Install GSS via pip:

```bash
git clone https://github.com/tsaol/GSS.git
cd GSS
pip install -e . 

# Install boto
pip install boto3
# Configure your AWS credentials
aws configure


```

Define your model configuration in a YAML file:

```yaml
envs:
  # MODEL_NAME: meta-llama/Meta-Llama-3-70B-Instruct
  MODEL_NAME: meta-llama/Meta-Llama-3-8B-Instruct
  HF_TOKEN: # TODO: Fill with your own huggingface token, or use --env to pass.

service:
  replicas: 2
  # An actual request for readiness probe.
  readiness_probe:
    path: /v1/chat/completions
    post_data:
      model: $MODEL_NAME
      messages:
        - role: user
          content: Hello! What is your name?
      max_tokens: 1

resources:
  cloud: aws
  region: us-east-1
  accelerators: {A10g:1}
  cpus: 8+
  use_spot: True
  disk_size: 512  # Ensure model checkpoints can fit.
  disk_tier: best
  ports: 8081  # Expose to internet traffic.

setup: |
  conda activate vllm
  if [ $? -ne 0 ]; then
    conda create -n vllm python=3.10 -y
    conda activate vllm
  fi

  pip install vllm==0.4.2
  # Install Gradio for web UI.
  pip install gradio openai
  pip install flash-attn==2.5.9.post1


run: |
  conda activate vllm
  echo 'Starting vllm api server...'

  python -u -m vllm.entrypoints.openai.api_server \
    --port 8081 \
    --model $MODEL_NAME \
    --trust-remote-code --tensor-parallel-size $SKYPILOT_NUM_GPUS_PER_NODE \
    --gpu-memory-utilization 0.95 \
    --max-num-seqs 64 \
    2>&1 | tee api_server.log &

  while ! `cat api_server.log | grep -q 'Uvicorn running on'`; do
    echo 'Waiting for vllm api server to start...'
    sleep 5
  done2

  echo 'Starting gradio server...'
  git clone https://github.com/vllm-project/vllm.git || true
  python vllm/examples/gradio_openai_chatbot_webserver.py \
    -m $MODEL_NAME \
    --port 8811 \
    --model-url http://localhost:8081/v1 \
    --stop-token-ids 128009,128001
  gss serve
```

Launch the inference endpoint:

```bash
#Start
HF_TOKEN=xxx sky serve up llama3.yaml -n llama3 --env HF_TOKEN
```

## 📃 License

GSS is open-source under the [Apache-2.0 License](LICENSE).
