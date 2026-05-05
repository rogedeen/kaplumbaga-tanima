import { Module } from '@nestjs/common';
import { TurtleService } from './turtle.service';
import { PrismaService } from '../prisma/prisma.service';

@Module({
  providers: [TurtleService, PrismaService],
  exports: [TurtleService],
})
export class TurtleModule {}
