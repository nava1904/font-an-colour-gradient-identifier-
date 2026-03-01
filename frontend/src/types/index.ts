export interface FontResult {
  label: string;
  confidence: number;
  alternatives: { label: string; score: number }[];
  error?: string;
}

export interface ColorFormat {
  hex: string;
  rgb: number[];
  hsl: number[];
}

export interface DominantColor extends ColorFormat {
  percentage: number;
}

export interface GradientStop extends ColorFormat {
  position: number;
}

export interface GradientResult {
  stops: GradientStop[];
  angle: number;
}

export interface SampledPoint extends ColorFormat {
  x: number;
  y: number;
}

export interface ColorsResult {
  dominant: DominantColor[];
  gradient: GradientResult;
  exact: { sampled_points: SampledPoint[] };
}

export interface AnalysisResult {
  font: FontResult;
  colors: ColorsResult;
}
