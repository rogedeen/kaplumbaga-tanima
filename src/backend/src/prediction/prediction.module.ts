import { Module } from '@nestjs/common';
import { PredictionController } from './prediction.controller';
import { PredictionService } from './prediction.service';
import { PythonInferenceEngine } from './python-inference.engine';

@Module({
  imports: [],
  controllers: [PredictionController],
  providers: [PredictionService, PythonInferenceEngine],
  exports: [PredictionService],
})
export class PredictionModule {}
