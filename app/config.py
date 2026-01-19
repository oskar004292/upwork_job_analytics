from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Upwork Jobs Statistics Bot"
    env: str = "prod"
    database_url: str = "sqlite:///./data.db"

    poll_interval_seconds: int = 120
    enable_scheduler: bool = True

    window_days_default: int = 7

    fit_stacks_csv: str = "react,next.js,typescript,node,php,wordpress"

    w_demand: float = 0.35
    w_price: float = 0.30
    w_competition: float = 0.20
    w_fit: float = 0.15

    read_only_mode: bool = False
    enable_inference: bool = True

settings = Settings()
