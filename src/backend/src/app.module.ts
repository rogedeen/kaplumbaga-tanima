import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { TurtleModule } from './turtle/turtle.module';
import { PredictionModule } from './prediction/prediction.module';

@Module({
  imports: [TurtleModule, PredictionModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
