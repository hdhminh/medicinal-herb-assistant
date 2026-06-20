# Medicinal Herb Assistant

This repository contains a team-built AI assistant for Vietnamese medicinal herbs. The system combines a FastAPI backend, a React frontend, a Gemini-powered Q&A flow, and a computer-vision pipeline for herb image recognition.

## Project Overview

The product was designed to help users:

- ask natural-language questions about Vietnamese medicinal herbs
- identify herbs from uploaded images
- review herb details such as common uses, usage guidance, and precautions
- browse supporting reference information through a web interface
- submit feedback for future iteration

At a system level, the repository contains three main parts:

1. `app/`
   FastAPI services and API routes for herb lookup, AI-generated answers, image-based prediction, and feedback handling.

2. `frontend/`
   A React client that provides the user-facing workflow for asking questions, browsing herb details, uploading images, and viewing results.

3. `CV_training/`
   A standalone computer-vision training pipeline for herb classification, including dataset loading, preprocessing, model definitions, training loops, and evaluation utilities.

## Core Capabilities

- Herb Q&A backed by structured herb data and Gemini-generated responses
- Image recognition flow for classifying medicinal herbs from user-provided photos
- Herb detail pages with descriptions, scientific names, usage notes, and image galleries
- Feedback submission flow for collecting user input
- Separate CV training workspace for model experimentation and iteration

## Tech Stack

### Backend

- Python
- FastAPI
- Uvicorn
- Google Generative AI / Gemini
- PyTorch
- Torchvision

### Frontend

- React
- React Router
- Axios
- React Icons
- React Select

### Machine Learning

- DINOv2-based classifier
- Custom CNN experimentation
- Local dataset and training utilities under `CV_training/`

## Repository Structure

```text
.
|-- app/                  FastAPI backend and herb data
|-- frontend/             React frontend
|-- CV_training/          Computer-vision training pipeline
|-- requirements.txt      Python dependencies
|-- package.json          Root-level JS dependencies used in the repo
`-- README.md
```

## My Contribution

This fork is used to document my contribution scope within the original team project.

My confirmed contribution in the visible git history is centered on the `CV_training/` module, especially the addition of the full herb-recognition training workspace. That contribution includes:

- adding the full `CV_training/` project structure
- adding model definitions for herb classification experiments
- adding dataset, preprocessing, and image utility code
- adding training and evaluation modules
- adding training metadata and supporting documentation for the CV pipeline

Evidence in git history:

- commit `ca79e6f` by `hdhminh` - `CV_training full folders.`
- commit `ca71036` by `hdhminh` - `CV_training full folders.`

This README does not present the full application as my sole work. The backend, frontend, and other implementation areas reflect collaboration across multiple contributors.

## Local Setup

### Backend

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm start
```

### CV Training

```bash
cd CV_training
pip install -r requirement.txt
python main.py
```
