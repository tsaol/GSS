<p align="center">
  <img alt="GSS Logo" src="https://raw.githubusercontent.com/gss-org/gss/master/docs/source/images/gss-logo.png" width="400px">
</p>

# GPU Spot Scheduler (GSS)

<p align="center">
  <a href="https://gss.readthedocs.io/en/latest/" target="_blank">
    <img src="https://readthedocs.org/projects/gss/badge/?version=latest" alt="Documentation Status" />
  </a>
  <a href="https://github.com/gss-org/gss/releases" target="_blank">
    <img src="https://img.shields.io/github/v/release/gss-org/gss" alt="GitHub release" />
  </a>
  <a href="https://github.com/gss-org/gss/blob/master/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/gss-org/gss" alt="License" />
  </a>
  <a href="https://slack.gss.co" target="_blank">
    <img src="https://img.shields.io/badge/slack-join_chat-white.svg?logo=slack&style=social" alt="Slack" />
  </a>
</p>

<p align="center">
  <b>LLM Inference and AI Workloads on AWS Spot GPUs</b>
</p>

GSS is a framework for efficient and cost-effective deployment of large language models (LLMs) and AI workloads on AWS spot GPU instances. Built upon [SkyPilot](https://github.com/skypilot-org/skypilot) v0.6, GSS inherits its powerful job orchestration capabilities.

## 🚀 Features

- **Optimized LLM Inference**: Integration with popular LLM frameworks, auto-batching, and model offloading for maximum GPU utilization.
- **Cost Savings**: Leverages cheap AWS spot instances for up to 90% cost reduction compared to on-demand.
- **Simplified Deployment**: Launch inference endpoints with a single command and automatic scaling.
- **Flexible Inference Modes**: Supports both real-time and offline batch inference.

## 📚 Documentation

- [Installation](https://gss.readthedocs.io/en/latest/getting-started/installation.html)
- [Quickstart](https://gss.readthedocs.io/en/latest/getting-started/quickstart.html)
- [Examples](https://github.com/gss-org/gss-examples)
- [CLI Reference](https://gss.readthedocs.io/en/latest/reference/cli.html)

## 🛠️ Quick Start

Install GSS via pip:

```bash
pip install gss
```

Define your model configuration in a YAML file:

```yaml
model:
  name: gpt-j-6b
  framework: transformers

resources:
  accelerators: A100:1

deployment:  
  type: endpoint
  min_replicas: 1
  max_replicas: 10
  
batching:
  max_batch_size: 8
  max_latency: 100  

run: |  
  gss serve
```

Launch the inference endpoint:

```bash
gss launch endpoint.yaml
```

## 🌐 AWS Integration

GSS seamlessly integrates with AWS, enabling you to deploy LLM inference workloads on cost-effective spot GPU instances.

<p align="center">
  <img src="https://raw.githubusercontent.com/gss-org/gss/master/docs/source/images/aws-logo.png" alt="AWS Integration" width="200px">
</p>

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING](CONTRIBUTING.md) to get started.

## 💬 Community

- [Twitter](https://twitter.com/gss_org)
- [Slack](https://slack.gss.co)
- [GitHub Discussions](https://github.com/gss-org/gss/discussions)

## 📃 License

GSS is open-source under the [Apache-2.0 License](LICENSE).
