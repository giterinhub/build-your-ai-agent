
# AI Agents

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg)](https://www.docker.com/)
[![Terraform](https://img.shields.io/badge/terraform-%235835CC.svg)](https://www.terraform.io/)

**AI Agents** is an advanced project leveraging the power of [Google's Gemini 1.5 Pro](https://developers.googleblog.com/en/gemini-15-pro-and-15-flash-now-available/) AI models. It offers:

* **[Function Calling](https://ai.google.dev/gemini-api/docs/function-calling):** Seamless integration of custom functions.
* **[RAG (Retrieval Augmented Generation)](https://cloud.google.com/vertex-ai/generative-ai/docs/llamaindex-on-vertexai):** Enhanced responses with external data context.

Built with Python, it utilizes [AlloyDB](https://cloud.google.com/alloydb) when deployed to Google Cloud and [AlloyDB Omni](https://cloud.google.com/alloydb/omni) for local development.


![AI Agent preview picture](static/images/ai_agent_demo.png "AI Agent preview picture")

## Features

* Cutting-edge AI (Gemini 2.0 Flash)
* Versatile capabilities (function calling, RAG, image generation)
* Robust storage (AlloyDB Omni)
* Streamlined deployment (Docker & Terraform)

## Getting Started

### Prerequisites

* Python 3.x
* Docker
* Terraform

### Local Setup

1. Clone this repository: `git clone git@github.com:NucleusEngineering/ai-agents.git`
2. Set environment variables:
   ```bash
   export PROJECT_ID=your-gcp-project-id
   export REGION=your-gcp-region
   ```
3. Start the Docker containers: docker compose up -d
4. Access the application at: http://localhost:8080   

### Remote Deployment

1. Navigate to `terraform` folder.
2. Customize `terraform.tfvars` based on `terraform.tfvars.template`.
3. Run: `terraform init`, `terraform plan`, `terraform apply`
4. In the root project folder, execute Cloud Build: `gcloud builds submit --config cloudbuild.yaml --substitutions _SERVICE_NAME=your-service-name,_REGION=your-gcp-region`
5. Get the URL where the demo was deployed: `gcloud run services list | grep -i ai-agent`

## Usage

You can interact with the AI Agent both via writing. 

Information that AI Agent can discuss with you is:

* **Google Cloud:**  Get the information about Google Cloud's serverless technology. E.g.: `What are Cloud Functions good for?`
* **Support Tickets:** Need help? Check the status of your support tickets right here. E.g.: `What are my support tickets?`
* **Generate new avatar:**  Get a new avatar with help of Generative AI. E.g.: `Create me a new avatar that looks like an orange cat.`
* **Ask specific questions (RAG):**  Get grounded answers based on the specific documents supplied to Gemini. E.g.: `What do you know about an amazing Digital Natives team at Google Cloud?`
* **Try multiple languages:**  Speak with the model in any language you know! E.g.: `Explica-me como function Cloud Run por favor.` (pt-PT)

## License

Apache License 2.0. See the [LICENSE](LICENSE) file.
