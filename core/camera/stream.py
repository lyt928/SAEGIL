from dataclasses import dataclass


@dataclass
class CameraConfig:
    source: int | str = 0
    width: int = 1280
    height: int = 720
    fps: int = 30


def describe_camera(config: CameraConfig) -> dict:
    return {
        "source": config.source,
        "width": config.width,
        "height": config.height,
        "fps": config.fps,
    }
