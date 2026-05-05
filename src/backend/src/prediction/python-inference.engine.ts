import { Injectable, Logger } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';
import { IInferenceEngine, InferenceResult } from './prediction.interface';

const execAsync = promisify(exec);

@Injectable()
export class PythonInferenceEngine implements IInferenceEngine {
  private readonly logger = new Logger(PythonInferenceEngine.name);

  async runInference(imagePath: string): Promise<InferenceResult> {
    // Proje kök dizinini bul (src/backend/ dizinindeyiz, bir üst dizin ana kök)
    const rootDir = path.resolve(process.cwd(), '..');
    const pythonPath = path.join(rootDir, '..', '.venv', 'Scripts', 'python');
    const scriptPath = path.join(rootDir, 'evaluate_single_image.py');
    
    try {
      this.logger.log(`Executing Python script: ${scriptPath} using ${pythonPath}`);
      
      const { stdout, stderr } = await execAsync(`"${pythonPath}" "${scriptPath}" "${imagePath}"`);
      
      if (stderr) {
        this.logger.warn(`Python stderr: ${stderr}`);
      }

      const output = stdout.trim();
      const resultRaw = JSON.parse(output);

      return {
        turtleId: resultRaw.pred || resultRaw.turtle_id || null,
        confidence: resultRaw.conf || resultRaw.confidence || 0,
        findings: resultRaw.info ? [resultRaw.info] : [],
        warnings: resultRaw.error ? [resultRaw.error] : [],
        ok: !resultRaw.error,
        raw: resultRaw,
      };
    } catch (error) {
      this.logger.error(`Inference failed: ${error.message}`);
      return {
        turtleId: null,
        confidence: 0,
        findings: [],
        warnings: [error.message],
        ok: false,
      };
    }
  }
}
