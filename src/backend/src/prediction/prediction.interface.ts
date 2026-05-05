export interface InferenceResult {
  turtleId: string | null;
  confidence: number;
  findings: string[];
  warnings: string[];
  ok: boolean;
  raw?: any;
}

export interface IInferenceEngine {
  runInference(imagePath: string): Promise<InferenceResult>;
}
