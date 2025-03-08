# GenMedia Studio

GenMedia Studio is a web application built for creative & marketing teams providing a user-friendly way to access and interact with Google Cloud Vertex AI's generative AI creative APIs with a focus on streamlining image and video generation and editing.

## Overview

GenMedia Studio addresses the challenges of efficiently creating high-quality images for various use cases, such as display campaigns, website content, and more. It aims to improve the efficiency and quality of AI-generated images.

This solution employs a modular microservices architecture to ensure scalability, maintainability, and expandability. Each service is designed to handle specific tasks, allowing for independent scaling and updates.

## Features

GenMedia Studio provides a rich set of features, including:

* **Image Generation:** Generate high-quality images using Imagen3 and Imagen3 Fast models, with support for preset modifiers to control the output, as well as the ability to provide reference images.
   
* **Prompt Rewriting:** Refine and enhance your text prompts using Google Gemini to achieve better image generation results.
   
* **Customizable Image Critique/Evaluation:** Evaluate generated images based on specific criteria or personas, using the power of Google Gemini to provide detailed feedback.
   
* **Mask-Based Image Editing:** Precisely edit images using Imagen3's masking capabilities and segmentation models for tasks like inpainting, outpainting, and object removal.
   
* **Image Storage and Metadata:** Store generated and edited images along with their associated metadata for easy retrieval and management.
   
* **Multimodal Image Search:** Search for images using text queries, leveraging multimodal embeddings to combine semantic and keyword search capabilities.

## Architecture

GenMedia Studio is built using a microservices architecture on Google Cloud. Key components include:

* **GenMedia Frontend:** A web application built with Mesop, providing a user-friendly interface for interacting with the various services.
   
* **API Gateway:** The central entry point for the application, routing requests to the appropriate backend services. 
   
* **Microservices:**
    * **Generation Service:** Handles image generation and editing requests, leveraging Vertex AI's Imagen models. 
    * **File Service:** Manages the storage and retrieval of images and related files, using Google Cloud Storage. 

The architecture is designed for scalability, maintainability, and the ability to easily add new features.

## Getting Started

### Prerequisites

*   A **Google Cloud project**:
    *   `Owner` permissions for the user installing the application
    *   Configured `OAuth Consent Screen` set to `INTERNAL`.
    *   Configured `Docker` by running the following once:
        
        `gcloud auth configure-docker us-central1-docker.pkg.dev --quiet`

### Installation

```
git clone <repo_url>
cd genmedia-studio
gcloud builds submit --config cloudbuild.yaml .
```

## Disclaimer

This is not an officially supported Google product.
