import re
import math
import json
import asyncio
from typing import Optional
from datetime import datetime
import httpx

# Standard constants for AI cliché phrase detection
ENGLISH_CLICHES = (
    r"\bin conclusion\b",
    r"\bit is important to note\b",
    r"\bit is worth noting\b",
    r"\bdelve(?:s|d)? into\b",
    r"\ba testament to\b",
    r"\bcrucial role\b",
    r"\btapestry of\b",
    r"\bbeacon of\b",
    r"\bfurthermore\b",
    r"\bmoreover\b",
    r"\bnavigating the landscape\b",
    r"\bin summary\b",
    r"\bfostering\b",
    r"\bgame-changer\b",
    r"\bdive deep(?:ly)?\b",
    r"\bharness(?:ing)? the power of\b",
    r"\bplays a pivotal role\b",
    r"\bin the realm of\b",
)

INDONESIAN_CLICHES = (
    r"\btentu saja\b",
    r"\boleh karena itu\b",
    r"\bpenting untuk dicatat(?: bahwa)?\b",
    r"\bperlu diingat(?: bahwa)?\b",
    r"\bberperan penting\b",
    r"\bmemainkan peran penting\b",
    r"\bdalam era modern ini\b",
    r"\bdalam lanskap\b",
    r"\bsebagai kesimpulan\b",
    r"\bmenjadi bukti(?: bahwa)?\b",
    r"\bmerupakan hal yang krusial\b",
    r"\btidak dapat dipungkiri bahwa\b",
    r"\bmenyelami lebih dalam\b",
    r"\bdalam rangka untuk\b",
    r"\bsecara keseluruhan\b",
    r"\bpatut digarisbawahi\b",
)

COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in ENGLISH_CLICHES + INDONESIAN_CLICHES]

# Processing limits for chunked execution
CHUNK_WORD_LIMIT = 500
MAX_OUTPUT_TOKENS = 8192
BASE_SCORE = 75
CLICHE_WEIGHT = 8
MAX_PENALTY = 40
BURST_THRESHOLD = 7.0
BURST_BONUS = 15
FLAT_PENALTY = 10
TARGET_HUMAN_SCORE = 85
REFINEMENT_TEMPERATURE = 0.85

SYSTEM_PROMPT = """You are an elite bilingual human editor and writer. Your task is to rewrite AI-generated text into genuinely natural, authentic human writing while preserving the full depth, volume, and structure of the original work.

Core Directives:
1. Balanced Output Volume:
   - Do NOT summarize, compress, or condense the content.
   - Preserve all ideas, arguments, explanations, nuances, and paragraph structures.
   - The resulting word count should be balanced and closely match the length of the source text (~1:1 ratio).

2. Human Flow & Fluency (Luwes):
   - Replace mechanical AI sentence transitions (e.g., "Tentu saja", "Perlu diingat bahwa", "Dalam era modern ini", "Secara keseluruhan", "Furthermore", "In conclusion") with natural, organic phrasings.
   - Vary sentence cadence naturally: blend short, rhythmic statements with fluid, well-structured explanatory sentences.
   - Use authentic human vocabulary and idioms suitable to the language of the source text (Indonesian or English).

3. Content Fidelity:
   - Retain every single fact, technical detail, step, and meaning from the original text without introducing unrelated assumptions.

4. Output Format:
   - Output strictly the humanized text. Do not include introductory remarks, commentary, or markdown code fences."""


def logMessage(messageText: str) -> None:
    # Print formatted log according to rule standard
    currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"({currentTime}) {messageText}")


def splitSentences(sourceText: str) -> list[str]:
    # Split text into clean sentences by punctuation
    rawSentences = re.split(r'(?<=[.!?])\s+', sourceText.strip())
    return [sentence.strip() for sentence in rawSentences if sentence.strip()]


def chunkParagraphs(sourceText: str, wordLimit: int = CHUNK_WORD_LIMIT) -> list[str]:
    # Split text into distinct paragraphs
    rawParagraphs = re.split(r'\n\s*\n', sourceText.strip())
    cleanParagraphs = [paragraph.strip() for paragraph in rawParagraphs if paragraph.strip()]

    # Early return if single paragraph or empty
    if not cleanParagraphs:
        return [sourceText]

    textChunks = []
    currentParagraphs = []
    currentWords = 0

    # Group paragraphs while respecting word limit
    for paragraphText in cleanParagraphs:
        paragraphCount = len(re.findall(r'\b\w+\b', paragraphText))

        # Check if adding current paragraph exceeds target limit
        if currentParagraphs and (currentWords + paragraphCount > wordLimit):
            textChunks.append("\n\n".join(currentParagraphs))
            currentParagraphs = [paragraphText]
            currentWords = paragraphCount
        else:
            currentParagraphs.append(paragraphText)
            currentWords += paragraphCount

    # Append trailing accumulated paragraphs
    if currentParagraphs:
        textChunks.append("\n\n".join(currentParagraphs))

    return textChunks


def analyzeText(sourceText: str) -> dict:
    # Guard clause for empty input
    if not sourceText.strip():
        return {
            "wordCount": 0,
            "sentenceCount": 0,
            "burstinessScore": 0,
            "clicheCount": 0,
            "humanScore": 100,
            "verdictText": "No text provided",
            "flaggedSentences": [],
        }

    # Extract words and count sentences
    extractedWords = re.findall(r'\b\w+\b', sourceText.lower())
    wordCount = len(extractedWords)
    sentenceList = splitSentences(sourceText)
    sentenceCount = len(sentenceList)

    # Compute sentence lengths and burstiness standard deviation
    lengthList = [len(re.findall(r'\b\w+\b', sentence)) for sentence in sentenceList]
    averageLength = sum(lengthList) / max(1, sentenceCount)
    varianceValue = sum((length - averageLength) ** 2 for length in lengthList) / max(1, sentenceCount)
    standardDeviation = math.sqrt(varianceValue)
    burstinessScore = min(100, round(standardDeviation * 8.5))

    # Detect known AI cliché patterns and identify flagged sentences
    detectedList = []
    flaggedSentences = []
    for sentenceItem in sentenceList:
        sentenceMatches = []
        for pattern in COMPILED_PATTERNS:
            foundPatterns = pattern.findall(sentenceItem)
            if foundPatterns:
                sentenceMatches.extend(foundPatterns)
        if sentenceMatches:
            detectedList.extend(sentenceMatches)
            flaggedSentences.append(sentenceItem)

    clicheCount = len(detectedList)

    # Calculate human authenticity score
    clichePenalty = min(MAX_PENALTY, clicheCount * CLICHE_WEIGHT)
    burstinessBonus = BURST_BONUS if standardDeviation >= BURST_THRESHOLD else (-FLAT_PENALTY if standardDeviation < 3.0 and sentenceCount > 2 else 0)
    calculatedScore = max(10, min(98, BASE_SCORE - clichePenalty + burstinessBonus))

    # Assign descriptive verdict
    if calculatedScore >= 80:
        verdictText = "Natural Human"
    elif calculatedScore >= 55:
        verdictText = "Mixed Elements"
    else:
        verdictText = "AI Pattern"

    return {
        "wordCount": wordCount,
        "sentenceCount": sentenceCount,
        "burstinessScore": burstinessScore,
        "clicheCount": clicheCount,
        "humanScore": calculatedScore,
        "verdictText": verdictText,
        "flaggedSentences": flaggedSentences,
    }


async def executePrompt(
    sourceText: str,
    providerUrl: str,
    apiKey: str,
    toneValue: str = "natural",
    modelName: str = "claude-opus-5",
    timeoutSeconds: float = 60.0,
    temperatureValue: float = 0.75,
    customInstruction: Optional[str] = None
) -> str:
    # Use custom instruction if provided, else construct tone guidance
    if customInstruction:
        userContent = customInstruction
    else:
        toneDescriptions = {
            "natural": "Natural and conversational human tone.",
            "academic": "Rigorous academic style, scholarly yet fluid.",
            "business": "Polished workplace tone, articulate and persuasive.",
            "casual": "Relaxed and expressive tone, very approachable.",
        }
        toneGuide = toneDescriptions.get(toneValue.lower(), toneDescriptions["natural"])

        userContent = (
            f"Tone style: {toneGuide}\n\n"
            f"Please rewrite the following text with human fluency while maintaining its full depth, details, and length:\n\n"
            f"{sourceText}"
        )

    payloadData = {
        "model": modelName,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": userContent}
        ],
        "temperature": temperatureValue,
        "max_tokens": MAX_OUTPUT_TOKENS,
        "stream": False,
    }

    headerData = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {apiKey}" if apiKey else ""
    }

    endpointUrl = f"{providerUrl.rstrip('/')}/chat/completions"

    # Execute asynchronous HTTP request with configured timeout
    async with httpx.AsyncClient(timeout=timeoutSeconds) as httpClient:
        responseObject = await httpClient.post(endpointUrl, headers=headerData, json=payloadData)

        # Check HTTP status
        if responseObject.status_code != 200:
            logMessage(f"Provider error received: status {responseObject.status_code}")
            raise ValueError(f"Provider API returned status {responseObject.status_code}: {responseObject.text}")

        contentType = responseObject.headers.get("content-type", "")
        responseText = responseObject.text.strip()

        # Handle Server-Sent Events stream format if returned
        if "text/event-stream" in contentType or responseText.startswith("data:"):
            collectedFragments = []
            for streamLine in responseText.splitlines():
                cleanLine = streamLine.strip()
                if not cleanLine.startswith("data:"):
                    continue
                chunkPayload = cleanLine[5:].strip()
                if chunkPayload == "[DONE]":
                    break
                try:
                    chunkData = json.loads(chunkPayload)
                    deltaObject = chunkData.get("choices", [{}])[0].get("delta", {})
                    deltaContent = deltaObject.get("content", "")
                    if deltaContent:
                        collectedFragments.append(deltaContent)
                except json.JSONDecodeError:
                    continue
            if collectedFragments:
                return "".join(collectedFragments).strip()

        # Parse standard JSON response
        try:
            responseData = responseObject.json()
        except Exception as jsonError:
            logMessage("Failed to parse provider JSON response")
            raise ValueError(f"Provider returned invalid response format: {responseText[:200]}") from jsonError

        # Extract response content safely
        return responseData["choices"][0]["message"]["content"].strip()


async def requestHumanization(
    sourceText: str,
    providerUrl: str,
    apiKey: str,
    toneValue: str = "natural",
    modeValue: str = "fast",
    modelName: str = "claude-opus-5",
    timeoutSeconds: float = 60.0,
    temperatureValue: float = 0.75
) -> str:
    # Validate provider URL before executing
    if not providerUrl:
        logMessage("Execution failed: Missing provider URL")
        raise ValueError("Provider URL is required for OpenAI-compatible endpoint")

    # Split source text into balanced paragraph chunks
    textChunks = chunkParagraphs(sourceText, CHUNK_WORD_LIMIT)
    totalChunks = len(textChunks)

    # Execute Pass 1 (Drafting)
    if totalChunks == 1:
        logMessage(f"Starting text humanization with {modelName} in {modeValue} mode")
        draftText = await executePrompt(
            sourceText=sourceText,
            providerUrl=providerUrl,
            apiKey=apiKey,
            toneValue=toneValue,
            modelName=modelName,
            timeoutSeconds=timeoutSeconds,
            temperatureValue=temperatureValue
        )
    else:
        logMessage(f"Processing {totalChunks} text chunks concurrently in {modeValue} mode")
        chunkTasks = [
            executePrompt(
                sourceText=chunkText,
                providerUrl=providerUrl,
                apiKey=apiKey,
                toneValue=toneValue,
                modelName=modelName,
                timeoutSeconds=timeoutSeconds,
                temperatureValue=temperatureValue
            )
            for chunkText in textChunks
        ]
        processedChunks = await asyncio.gather(*chunkTasks)
        draftText = "\n\n".join(processedChunks)

    # Return draft immediately if fast mode is selected
    if modeValue != "deep":
        logMessage("Humanization completed via fast mode")
        return draftText

    # Audit draft for adversarial closed-loop evaluation
    auditMetrics = analyzeText(draftText)
    needsRefinement = (auditMetrics["humanScore"] < TARGET_HUMAN_SCORE) or bool(auditMetrics["flaggedSentences"])

    # Early return if draft already exceeds threshold
    if not needsRefinement:
        logMessage(f"Draft achieved human score {auditMetrics['humanScore']}. No refinement needed")
        return draftText

    # Execute Pass 2 (Adversarial Refinement)
    logMessage(f"Draft score {auditMetrics['humanScore']} below target {TARGET_HUMAN_SCORE}. Initiating refinement pass...")
    flaggedSample = "\n".join(f"- {sentence}" for sentence in auditMetrics["flaggedSentences"][:4])
    refineInstruction = (
        f"The following rewritten text is good, but these specific sentences still sound robotic or contain AI clichés:\n"
        f"{flaggedSample}\n\n"
        f"Please perform a second-pass polish. Restructure those stiff sentences into natural, organic human expressions with lively cadence, while keeping all facts, paragraph layout, and text volume:\n\n"
        f"{draftText}"
    )

    refinedText = await executePrompt(
        sourceText=draftText,
        providerUrl=providerUrl,
        apiKey=apiKey,
        toneValue=toneValue,
        modelName=modelName,
        timeoutSeconds=timeoutSeconds,
        temperatureValue=REFINEMENT_TEMPERATURE,
        customInstruction=refineInstruction
    )

    logMessage("Adversarial refinement pass completed successfully")
    return refinedText
