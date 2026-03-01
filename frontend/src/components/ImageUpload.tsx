"use client";

import { useCallback, useState } from "react";

interface ImageUploadProps {
  onUpload: (file: File) => void;
  disabled?: boolean;
}

export default function ImageUpload({ onUpload, disabled }: ImageUploadProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      if (disabled) return;
      const file = e.dataTransfer.files[0];
      if (file?.type.startsWith("image/")) {
        onUpload(file);
      }
    },
    [onUpload, disabled]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) onUpload(file);
    },
    [onUpload]
  );

  return (
    <label
      className={`
        flex min-h-[200px] cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed transition-colors
        ${isDragging ? "border-indigo-500 bg-indigo-50/50" : "border-zinc-300 hover:border-zinc-400"}
        ${disabled ? "cursor-not-allowed opacity-60" : ""}
      `}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <input
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif"
        onChange={handleChange}
        disabled={disabled}
        className="hidden"
      />
      <svg
        className="mb-3 h-12 w-12 text-zinc-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
        />
      </svg>
      <span className="text-sm font-medium text-zinc-600">
        Drop an image here or click to upload
      </span>
      <span className="mt-1 text-xs text-zinc-500">
        JPEG, PNG, WebP, GIF (max 10MB)
      </span>
    </label>
  );
}
