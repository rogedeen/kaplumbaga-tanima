import { ExceptionFilter, Catch, ArgumentsHost, HttpException, Logger } from '@nestjs/common';
import { Request, Response } from 'express';
import * as fs from 'fs';
import * as path from 'path';

@Catch(HttpException)
export class HttpExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(HttpExceptionFilter.name);

  catch(exception: HttpException, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();
    const status = exception.getStatus();
    const exceptionResponse = exception.getResponse();

    const errorLog = `[${new Date().toISOString()}] - HATA: ${status} - ${JSON.stringify(exceptionResponse)} - Path: ${request.url}\n`;
    const logPath = path.resolve(__dirname, '../../../../logs/backend.log');
    fs.appendFileSync(logPath, errorLog);

    this.logger.error(`HTTP Error: ${status} - ${request.url}`);

    response
      .status(status)
      .json({
        statusCode: status,
        timestamp: new Date().toISOString(),
        path: request.url,
        message: exceptionResponse['message'] || exception.message,
      });
  }
}
