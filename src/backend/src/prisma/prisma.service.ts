import { Injectable, OnModuleInit, Logger } from "@nestjs/common";
import { PrismaClient } from "@prisma/client";

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit {
  private readonly logger = new Logger(PrismaService.name);
  public connected = false;

  async onModuleInit() {
    try {
      // Attempt to connect to the database, but don't crash the whole app if unreachable.
      await this.$connect();
      this.connected = true;
      this.logger.log('Connected to database.');
    } catch (err) {
      this.connected = false;
      this.logger.warn('Prisma could not connect to the database. Continuing in degraded mode.');
      this.logger.debug(err instanceof Error ? err.message : String(err));
      // Do not rethrow — allow the app to start for MVP/demo purposes.
    }
  }

  // Optional helper to guard DB calls from other services
  isConnected(): boolean {
    return this.connected;
  }
}
