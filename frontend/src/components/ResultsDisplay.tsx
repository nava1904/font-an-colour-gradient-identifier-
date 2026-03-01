"use client";

import { useState } from "react";
import type { AnalysisResult, DominantColor, GradientStop, SampledPoint } from "@/types";

interface ResultsDisplayProps {
  result: AnalysisResult;
  imagePreview?: string;
}

function ColorSwatch({
  color,
  showCopy = true,
}: {
  color: { hex: string; rgb: number[] };
  showCopy?: boolean;
}) {
  const [copied, setCopied] = useState(false);

  const copyHex = () => {
    navigator.clipboard.writeText(color.hex);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="group flex flex-col items-center gap-1">
      <div
        className="h-12 w-12 rounded-lg border border-zinc-200 shadow-sm transition-transform hover:scale-105"
        style={{ backgroundColor: color.hex }}
      />
      {showCopy && (
        <button
          onClick={copyHex}
          className="text-xs text-zinc-600 hover:text-indigo-600"
          title="Copy hex"
        >
          {copied ? "Copied!" : color.hex}
        </button>
      )}
    </div>
  );
}

export default function ResultsDisplay({ result, imagePreview }: ResultsDisplayProps) {
  const { font, colors } = result;

  return (
    <div className="space-y-8">
      {/* Image preview */}
      {imagePreview && (
        <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
          <h3 className="mb-3 text-sm font-semibold text-zinc-700">Preview</h3>
          <img
            src={imagePreview}
            alt="Uploaded"
            className="max-h-64 rounded-lg object-contain"
          />
        </div>
      )}

      {/* Font result */}
      <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h3 className="mb-4 text-lg font-semibold text-zinc-800">Font</h3>
        {font.error ? (
          <p className="text-sm text-amber-600">{font.error}</p>
        ) : (
          <div>
            <p className="text-2xl font-medium text-indigo-600">{font.label}</p>
            <p className="mt-1 text-sm text-zinc-500">
              Confidence: {(font.confidence * 100).toFixed(1)}%
            </p>
            {font.alternatives.length > 0 && (
              <div className="mt-3">
                <p className="text-xs font-medium text-zinc-500">Alternatives</p>
                <ul className="mt-1 space-y-0.5 text-sm text-zinc-600">
                  {font.alternatives.map((a, i) => (
                    <li key={i}>
                      {a.label} ({(a.score * 100).toFixed(1)}%)
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Dominant colors */}
      <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h3 className="mb-4 text-lg font-semibold text-zinc-800">Dominant Colors</h3>
        <div className="flex flex-wrap gap-6">
          {colors.dominant.map((c: DominantColor, i: number) => (
            <div key={i} className="flex flex-col items-center gap-2">
              <ColorSwatch color={c} />
              <span className="text-xs text-zinc-500">{c.percentage}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Gradient */}
      <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h3 className="mb-4 text-lg font-semibold text-zinc-800">Gradient</h3>
        <div
          className="mb-4 h-16 w-full rounded-lg"
          style={{
            background: `linear-gradient(${colors.gradient.angle}deg, ${colors.gradient.stops
              .map((s) => `${s.hex} ${s.position}%`)
              .join(", ")})`,
          }}
        />
        <div className="flex flex-wrap gap-4">
          {colors.gradient.stops.map((s: GradientStop, i: number) => (
            <ColorSwatch key={i} color={s} />
          ))}
        </div>
      </div>

      {/* Exact sampled points */}
      <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h3 className="mb-4 text-lg font-semibold text-zinc-800">Exact Color Samples</h3>
        <div className="flex flex-wrap gap-6">
          {colors.exact.sampled_points.map((p: SampledPoint, i: number) => (
            <div key={i} className="flex flex-col items-center gap-1">
              <ColorSwatch color={p} />
              <span className="text-xs text-zinc-500">
                ({p.x}, {p.y})
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
