from pathlib import Path
from typing import Literal, List
from pydantic import BaseModel
from pydantic_settings import BaseSettings, DotEnvSettingsSource, EnvSettingsSource, SettingsConfigDict, PydanticBaseSettingsSource, YamlConfigSettingsSource
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


class PathsConfig(BaseModel):
    """Contains paths of directories"""
    project_dir: str
    models_dir: str
    # logs_dir: str

class YoloConfig(BaseModel):
    """Contains yolo configurations"""
    model_path: str
    classes: List[str]
    batch_size: int
    epochs: int
    wandb: bool
    augment: bool
    data_path: str

class SecurityDetector(BaseModel):
    "Contains Security Detectors like Smoke - Fire"
    model_path: str
    classes: List[str]

class DepthConfig(BaseModel):
    "Contains depths estimation configurations"
    model_path: str
    encoder: Literal["vits", "vitb", "vitl", "vitg"]

class IntervalsConfig(BaseModel):
    system_metrics_seconds: float
    frames_summary_every: int
    realtime_updates_every: float


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
        # case_sensitive=False,         # default True
        # env_prefix="YOLO_",         # Means configs we are talking about starts with YOLO_
        # env_nested_delimiter="__",  # Means we use _ instead of spaces for the same var
        extra="ignore"              # Ignore other settings in yaml and env as they are not mentioedhere
    )

    project_name:str
    project_desc:str
    task: Literal["indoor", "outdoor"]

    paths: PathsConfig
    yolo: YoloConfig
    security_detector: SecurityDetector
    depth: DepthConfig
    intervals: IntervalsConfig

    # Backend


    @classmethod
    def settings_customise_sources(cls, 
        settings_cls: type[BaseSettings],  # Base param.
        # init_settings: PydanticBaseSettingsSource,   # Values passed to __init__
        # env_settings: PydanticBaseSettingsSource,    # OS Env variables
        # dotenv_settings: PydanticBaseSettingsSource, 
        # file_secret_settings: PydanticBaseSettingsSource # Secret Directories
        **kwargs
        ) -> tuple[PydanticBaseSettingsSource, ...] :
        """
        Once you use this, no need to use load_config, it is already the same.
        But this time it fixs the priority part, order by parameters priority.  
        """

        # Order by priority
        return (
            DotEnvSettingsSource(settings_cls),    # Most important
            EnvSettingsSource(settings_cls),       # This allow for ex. hugging face to override .env values with its values. 
            YamlConfigSettingsSource(settings_cls), 
            )  # The return must be a tuple


    # @classmethod
    # def load_config(cls, yaml_path: Path | str = Path(__file__).parent / "config.yaml") -> "AppConfig":
    #     """Loading confiuration and settings from Config.yaml file then override using .env"""

    #     yaml_path = Path(yaml_path).resolve()  # Absolute path
    #     if not yaml_path.is_file():
    #         raise FileNotFoundError(f"Config file not found: {yaml_path}")

    #     with yaml_path.open("r") as f:
    #         yaml_data = yaml.safe_load(f) or {}

    #     # env_data = cls() # This one loaded .env and not Yaml
    #     # When this project grow, you are going to create different types of .yaml files for products and debugging and so on
    #     # Feel free to stack them here, so we use the yaml required for our testing
    #     # Note that in debuging.yaml file, we only override the base, not starting from scratch. 
    #     # return cls(**{
    #     #     **yaml_data,   # Loading config.yaml configurations
    #     #     # **env_data.model_dump()     # TODO(FIX) Overriding everything using .env
    #     #     })
    #     return cls(**yaml_data)




if __name__ == "__main__":  
    # Note that we must use AppConfig without () to take .env in mind.
    # Checking for YAML part.
    # config = AppConfig.load_config()
    # print(config.model_dump())
    # print(config.model_dump()["project_name"])

    # Checking for .env file. 
    # config = AppConfig()
    # print(f".env Path we are talking about: {Path(__file__).parent / ".env"}")
    # print(config.model_config)
    # print(config.project_name)

    # Trying to checking both yaml and .env.   This works really fine now. 
    config = AppConfig()
    print(config.model_dump())
    print(config.model_dump()["project_name"])