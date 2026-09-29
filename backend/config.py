import os
from pathlib import Path
from dotenv import load_dotenv

# Load central environment configuration from project root directory
rootDirectory = Path(__file__).resolve().parent.parent
load_dotenv(rootDirectory / ".env")


class ApplicationConfig:
    # Server network settings
    serverHost: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    serverPort: int = int(os.getenv("BACKEND_PORT", "8035"))
    allowedOrigins: list[str] = [
        origin.strip() for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:8085,http://127.0.0.1:8085"
        ).split(",") if origin.strip()
    ]

    # Secret vault and provider settings
    providerUrl: str = os.getenv("PROVIDER_URL", "")
    apiKey: str = os.getenv("API_KEY", "")
    modelName: str = os.getenv("MODEL_NAME", "claude-opus-5")

    # Engine limits and hyperparameters
    requestTimeout: float = float(os.getenv("REQUEST_TIMEOUT", "60.0"))
    modelTemperature: float = float(os.getenv("MODEL_TEMPERATURE", "0.75"))


applicationConfig = ApplicationConfig()
