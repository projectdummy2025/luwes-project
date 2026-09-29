from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import applicationConfig
from engine import analyzeText, requestHumanization, logMessage

# Initialize FastAPI application
applicationServer = FastAPI(title="Luwesin API", version="2.0.0")
app = applicationServer

# Setup CORS middleware for frontend communication
applicationServer.add_middleware(
    CORSMiddleware,
    allow_origins=applicationConfig.allowedOrigins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request schemas with strict types
class AnalysisRequest(BaseModel):
    sourceText: str = Field(..., min_length=1)


class HumanizeRequest(BaseModel):
    sourceText: str = Field(..., min_length=1)
    toneValue: str = Field(default="natural")
    modelName: Optional[str] = Field(default=None)
    providerUrl: Optional[str] = Field(default=None)
    apiKey: Optional[str] = Field(default=None)


@applicationServer.get("/api/config")
async def fetchConfiguration():
    # Return available configuration details
    hasServerKey = bool(applicationConfig.apiKey)
    hasServerUrl = bool(applicationConfig.providerUrl)

    return {
        "modelName": applicationConfig.modelName,
        "hasServerKey": hasServerKey,
        "hasServerUrl": hasServerUrl,
        "providerUrl": applicationConfig.providerUrl,
    }


@applicationServer.post("/api/analyze")
async def executeAnalysis(requestBody: AnalysisRequest):
    # Perform instant heuristic text analysis
    logMessage("Processing text analysis request")
    analysisData = analyzeText(requestBody.sourceText)
    return {"analysisData": analysisData}


@applicationServer.post("/api/humanize")
async def executeHumanization(requestBody: HumanizeRequest):
    # Determine effective provider URL, API key, and model name
    activeUrl = requestBody.providerUrl or applicationConfig.providerUrl
    activeKey = requestBody.apiKey or applicationConfig.apiKey
    activeModel = requestBody.modelName or applicationConfig.modelName

    # Guard clause if provider URL is missing
    if not activeUrl:
        raise HTTPException(
            status_code=400,
            detail="Provider URL is missing. Please provide it in settings or .env"
        )

    # Perform humanization using target model
    try:
        resultText = await requestHumanization(
            sourceText=requestBody.sourceText,
            providerUrl=activeUrl,
            apiKey=activeKey,
            toneValue=requestBody.toneValue,
            modelName=activeModel,
            timeoutSeconds=applicationConfig.requestTimeout,
            temperatureValue=applicationConfig.modelTemperature,
        )

        # Analyze resulting text for comparison
        resultAnalysis = analyzeText(resultText)

        return {
            "resultText": resultText,
            "resultAnalysis": resultAnalysis,
        }
    except ValueError as validationError:
        raise HTTPException(status_code=400, detail=str(validationError))
    except Exception as serverError:
        raise HTTPException(status_code=500, detail=f"Failed to process: {str(serverError)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:applicationServer",
        host=applicationConfig.serverHost,
        port=applicationConfig.serverPort,
        reload=True
    )
