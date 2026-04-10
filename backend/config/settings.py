from pathlib import Path
from typing import Literal, List
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)
import yaml


def join_tag(loader, node):
    """
    Help joining pathes in config.YAML directly.
    """
    parts = loader.construct_sequence(node)
    path = Path(*(str(part) for part in parts)).resolve()
    return str(path)


# It didn't work before, After some research, .SafeLoaded is unmentioned must for my case.
yaml.SafeLoader.add_constructor("!join", join_tag)


class IntervalsConfig(BaseModel):
    system_metrics_seconds: float
    frames_summary_every: int
    realtime_updates_every: float


class YoloConfig(BaseModel):
    """Contains yolo configurations"""

    model_name: str
    classes: List[str]
    batch_size: int
    epochs: int
    wandb: bool
    augment: bool
    data_path: str


class SecurityDetector(BaseModel):
    "Contains Security Detectors like Smoke - Fire"

    model_name: str
    classes: List[str]


class DepthConfig(BaseModel):
    "Contains depths estimation configurations"

    model_name: str
    device: Literal["cuda", "cpu"]
    encoder: Literal["vits", "vitb", "vitl", "vitg"]


class AppConfig(BaseSettings):
    """
    Main app Configuration
    - Gets defaults from config.yaml (via load_config)
    - Override values with .env
    """

    # Note that it doesn't show error, Take care.
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env",
        env_file_encoding="utf-8",
        yaml_file=Path(__file__).parent / "config.yaml",
        extra="ignore",  # Ignore other settings in yaml and env as they are not mentioedhere
    )

    project_name: str
    project_desc: str
    task: Literal["indoor", "outdoor"]

    yolo: YoloConfig
    security_detector: SecurityDetector
    depth: DepthConfig
    intervals: IntervalsConfig
    redis_url: str
    dagshub_user_token: str
    hf_cache_dir: str

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],  # Base param.
        **kwargs,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Once you use this, no need to use load_config, it is already the same.
        But this time it fixs the priority part, order by parameters priority.
        """

        # Order by priority (first, more important)
        return (
            DotEnvSettingsSource(settings_cls),  # Most important
            EnvSettingsSource(
                settings_cls
            ),  # This allow for ex. hugging face to override .env values with its values.
            YamlConfigSettingsSource(settings_cls),
        )  # The return must be a tuple


if __name__ == "__main__":
    # Trying to checking both yaml and .env.   This works really fine now.
    config = AppConfig()
    print(config.model_dump())
    print(config.model_dump()["project_name"])
