import { Controller, Post, UseInterceptors, UploadedFile, HttpException, HttpStatus } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { PredictionService } from './prediction.service';
import { diskStorage } from 'multer';
import { extname } from 'path';
import { unlink } from 'fs/promises';

@Controller('api')
export class PredictionController {
  constructor(private readonly predictionService: PredictionService) {}

  @Post('predict')
  @UseInterceptors(FileInterceptor('image', {
    storage: diskStorage({
      destination: './uploads',
      filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
        cb(null, `${uniqueSuffix}${extname(file.originalname)}`);
      },
    }),
  }))
  async uploadAndPredict(@UploadedFile() file: Express.Multer.File) {
    if (!file) {
      throw new HttpException('Görüntü dosyası gereklidir.', HttpStatus.BAD_REQUEST);
    }

    try {
      const result = await this.predictionService.predict(file.path);
      return result;
    } catch (error) {
      throw new HttpException(
        `Tahmin işlemi sırasında hata oluştu: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    } finally {
      // Geçici dosyayı temizle (Best practice)
      await unlink(file.path).catch(() => undefined);
    }
  }
}
