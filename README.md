# Font and Color Identifier

A webapp that uses ML/AI to identify fonts and extract colors (dominant, gradient, exact) from images.

## Features

- **Font identification**: DINOv2-based classifier (~86% accuracy, 394 Google Fonts)
- **Dominant colors**: K-means in LAB color space for perceptual accuracy
- **Gradient extraction**: Color stops with positions and angle
- **Exact color codes**: Pixel-level sampling with HEX, RGB, HSL

## Quick Start

### Backend (Python)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

If the full install fails (e.g. disk space), use color-only mode:
```bash
pip install -r requirements-color-only.txt
```
Font ID will show "unavailable" but colors work.

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The frontend proxies requests to the backend at `http://localhost:8000`.

**Note:** Both backend and frontend must be running. If analysis is stuck, ensure the backend is running and has dependencies installed (`pip install -r requirements.txt`). The font model downloads on first use (~2–5 min); color extraction returns within seconds.

### Environment

- `BACKEND_URL` (frontend `.env`): Backend API URL for the proxy (default: `http://localhost:8000`)

## API

- `POST /api/analyze` – Upload an image (multipart/form-data, field: `image`). Returns font and color analysis.
- `GET /health` – Health check

## Tech Stack

- **Backend**: FastAPI, OpenCV, scikit-image, Hugging Face Transformers (font classifier)
- **Frontend**: Next.js, TypeScript, Tailwind CSS
