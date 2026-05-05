import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class TurtleService {
  private readonly logger = new Logger(TurtleService.name);
  constructor(private prisma: PrismaService) {}

  async findAll() {
    return this.prisma.turtle.findMany({
      include: { images: true },
    });
  }

  async findOne(id: string) {
    return this.prisma.turtle.findUnique({
      where: { id },
      include: { images: true, predictions: true },
    });
  }

  async createTurtle(data: { name: string; tag?: string; description?: string }) {
    return this.prisma.turtle.create({
      data,
    });
  }

  async addImage(turtleId: string, url: string) {
    return this.prisma.image.create({
      data: {
        url,
        turtleId,
      },
    });
  }

  async savePrediction(data: { imageUrl: string; resultJson: any; confidence: number; turtleId?: string }) {
    if (!this.prisma.isConnected()) {
      this.logger.warn('Prisma not connected — skipping DB save for prediction (degraded mode).');
      // Return a minimal stub so callers can continue
      return { id: null, ...data, createdAt: new Date().toISOString() };
    }
    return this.prisma.prediction.create({
      data,
    });
  }
}
