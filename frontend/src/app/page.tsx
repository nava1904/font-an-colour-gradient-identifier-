"use client";

import { useState } from "react";
import ImageUpload from "@/components/ImageUpload";
import ResultsDisplay from "@/components/ResultsDisplay";
import type { AnalysisResult } from "@/types";

// Use same-origin API route (proxies to backend) to avoid CORS
const API_URL = "";

export default function Home() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (file: File) => {
    setError(null);
    setResult(null);

    const MAX_SIZE = 10 * 1024 * 1024; // 10MB
    if (file.size > MAX_SIZE) {
      setError("File too large. Maximum size is 10MB.");
      return;
    }

    setImagePreview(URL.createObjectURL(file));
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("image", file);

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 90000); // 90s timeout

      const res = await fetch(`${API_URL || ""}/api/analyze`, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "Analysis failed");
      }

      const data: AnalysisResult = await res.json();
      setResult(data);
    } catch (e) {
      const msg =
        e instanceof Error ? e.message : "Something went wrong";
      setError(
        msg.includes("fetch") ||
          msg.includes("Failed to fetch") ||
          msg.includes("Backend not running")
          ? "Backend not running. Start it with: cd backend && uvicorn app.main:app --reload --port 8000"
          : msg
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-50 via-white to-indigo-50/30">
      <main className="mx-auto max-w-2xl px-6 py-12">
        <header className="mb-10 text-center">
          <h1 className="text-3xl font-bold tracking-tight text-zinc-900">
            Font & Color Identifier
          </h1>
          <p className="mt-2 text-zinc-600">
            Upload an image to identify fonts and extract dominant colors, gradients, and exact
            color codes
          </p>
        </header>

        <ImageUpload onUpload={handleUpload} disabled={loading} />

        {loading && (
          <div className="mt-6 flex items-center justify-center gap-2 rounded-xl border border-zinc-200 bg-white py-8">
            <svg
              className="h-6 w-6 animate-spin text-indigo-600"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span className="text-zinc-600">Analyzing image...</span>
          </div>
        )}

        {error && (
          <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
            {error}
          </div>
        )}

        {result && !loading && (
          <div className="mt-8">
            <ResultsDisplay result={result} imagePreview={imagePreview || undefined} />
          </div>
        )}
      </main>
    </div>
  );
}
