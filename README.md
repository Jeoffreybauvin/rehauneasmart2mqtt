[![GitHub release]https://img.shields.io/github/v/release/Jeoffreybauvin/rehauneasmart2mqtt.svg?style=flat-square)](https://github.com/Jeoffreybauvin/rehauneasmart2mqtt/releases/latest) | ![Docker Image Version](https://img.shields.io/docker/v/jeoffrey54/rehauneasmart2mqtt)


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

## Deployment

The Docker image is automatically built and pushed to Docker Hub via GitHub Actions.

To enable this, the following secrets must be configured in the GitHub repository:
- `DOCKERHUB_USERNAME`: Your Docker Hub username.
- `DOCKERHUB_TOKEN`: Your Docker Hub access token (or password).

### Creating a Release

To trigger a new Docker image build with a version tag:

1. Create a git tag (must start with `v`, e.g., `v1.0.0`):
   ```bash
   git tag v1.0.0
   ```
2. Push the tag to GitHub:
   ```bash
   git push origin v1.0.0
   ```

This will automatically build and push Docker images tagged with `1.0.0`, `1.0`, and `latest` (if on the default branch).
