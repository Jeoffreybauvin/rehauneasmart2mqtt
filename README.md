# rehauneasmart2mqtt
Rehau Nea Smart to MQTT

## Development Environment

To start the development environment locally (Broker + Application), run:

```bash
docker-compose -f docker-compose.dev.yml up -d --build
```

The broker will be available on `localhost:1883`.

### Configuration Overrides

You can override environment variables (like `REHAU_HOST`) by creating a `.env` file in the root directory. This file is ignored by git.

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` with your specific configuration (e.g. set `REHAU_HOST` to your device's IP).
