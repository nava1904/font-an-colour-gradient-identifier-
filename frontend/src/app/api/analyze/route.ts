import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const image = formData.get("image");

    if (!image || !(image instanceof Blob)) {
      return NextResponse.json(
        { detail: "No image file provided" },
        { status: 400 }
      );
    }

    const backendFormData = new FormData();
    backendFormData.append("image", image);

    const res = await fetch(`${BACKEND_URL}/api/analyze`, {
      method: "POST",
      body: backendFormData,
      headers: {
        // Don't set Content-Type - FormData sets it with boundary
      },
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      return NextResponse.json(
        { detail: data.detail || res.statusText },
        { status: res.status }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Failed to reach backend";
    return NextResponse.json(
      {
        detail:
          message.includes("fetch") || message.includes("ECONNREFUSED")
            ? "Backend not running. Start it with: cd backend && uvicorn app.main:app --reload --port 8000"
            : message,
      },
      { status: 500 }
    );
  }
}
