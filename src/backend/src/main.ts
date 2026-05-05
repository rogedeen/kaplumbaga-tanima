import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { HttpExceptionFilter } from './common/filters/http-exception.filter';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // Apply global exception filter
  app.useGlobalFilters(new HttpExceptionFilter());
  
  // Enable CORS for frontend
  app.enableCors();
  
  await app.listen(3000);
  console.log('Backend application is running on: http://localhost:3000');
}
bootstrap();
