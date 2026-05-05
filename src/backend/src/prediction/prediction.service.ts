import { Injectable, Logger } from '@nestjs/common';
import { TurtleService } from '../turtle/turtle.service';
import { PythonInferenceEngine } from './python-inference.engine';
import { InferenceResult } from './prediction.interface';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class PredictionService {
  private readonly logger = new Logger(PredictionService.name);
  private readonly logFilePath = path.resolve(process.cwd(), '..', 'logs', 'prediction_audit.log');

  constructor(
    private readonly inferenceEngine: PythonInferenceEngine,
    private readonly turtleService: TurtleService,
  ) {
    // Ensure logs directory exists
    const logDir = path.dirname(this.logFilePath);
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }
  }

  async predict(imagePath: string): Promise<InferenceResult> {
    this.logger.log(`Prediction request received for: ${imagePath}`);

    // 1. Run Inference (SRP: Logic delegated to engine)
    const result = await this.inferenceEngine.runInference(imagePath);

    // 2. Persist to DB (SRP: Logic delegated to turtleService)
    await this.turtleService.savePrediction({
      imageUrl: imagePath,
      resultJson: result.raw,
      confidence: result.confidence,
      turtleId: result.turtleId,
    }).catch(err => this.logger.error(`DB Save failed: ${err.message}`));

    // 3. Audit Logging (Academic requirement)
    this.auditLog(imagePath, result);

    return result;
  }

  private auditLog(imagePath: string, result: InferenceResult) {
    const timestamp = new Date().toISOString();
    const status = result.ok ? 'SUCCESS' : 'FAILED';
    const logMessage = `[${timestamp}] [${status}] Image: ${path.basename(imagePath)} | Pred: ${result.turtleId} | Conf: ${result.confidence}\n`;
    
    try {
      fs.appendFileSync(this.logFilePath, logMessage);
    } catch (err) {
      this.logger.error(`Audit log failed: ${err.message}`);
    }
  }
}
