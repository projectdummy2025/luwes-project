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
    r"\bhakekat seorang\b",
    r"\bmerupakan sang\b",
    r"\bsebuah titik temu\b",
    r"\bproses menjadi\b",
    r"\bpuing-puing kegagalan\b",
    r"\bpustaka besar\b",
    r"\bbentangan kesadaran\b",
)

COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in ENGLISH_CLICHES + INDONESIAN_CLICHES]

# Structural AI fingerprint patterns
MARKDOWN_PATTERN = re.compile(r'\*\*([^*]+)\*\*|\*([^*]+)\*|__([^_]+)__|_([^_]+)_')
ANTITHESIS_PATTERN = re.compile(r'\b(?:bukan|tidak)\b.+?\b(?:melainkan)\b', re.IGNORECASE)
TRIAD_PATTERN = re.compile(r'\b\w+,\s+\w+,\s+(?:dan|atau|serta)\s+\w+', re.IGNORECASE)
CALQUE_PATTERN = re.compile(r'\b(?:ruang|tempat|kondisi|situasi|lingkungan|wadah)\s+di mana\b', re.IGNORECASE)
COPULA_PATTERN = re.compile(r'\b(?:adalah|merupakan)\b', re.IGNORECASE)

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

SYSTEM_PROMPT = """You are an experienced human author and editor. Your task is to rewrite AI-generated text into authentic, grounded human writing while preserving the full depth, volume, and structure of the original work.

Core Directives:
1. Balanced Output Volume:
   - Do NOT summarize, compress, or condense the content.
   - Preserve all ideas, arguments, explanations, nuances, and paragraph structures.
   - The resulting word count should closely match the source text (~1:1 ratio).

2. Natural Human Syntax (Anti-AI Fingerprints):
   - NO Markdown Formatting: Never use bold (**text**) or italics (*text*) for emphasis anywhere in the body text. Output plain prose only.
   - Break Triadic Parallelism: Avoid listing things in rigid groups of three (e.g., "A, B, dan C" or "X, Y, atau Z"). Use varied groupings, natural narrative flow, or direct statements.
   - Minimize Copulas: Drastically limit static definitional patterns ("X adalah Y", "X merupakan Y"). Use lively active verbs and varied sentence openers.
   - Eliminate Repetitive Antithesis: Do not repeat formulaic contrast structures ("bukan X, melainkan Y").
   - Eliminate Foreign Translationese (Calques): In Indonesian, never use "di mana" as a relative conjunction for places or situations. Use natural connectors like "tempat", "saat", "ketika", or rephrase.
   - Grounded Style: Avoid melodramatic, hyper-sentimental essay prose ("purple prose") or grandiose cosmic clichés. Write with concrete, earthy clarity.
   - Varied Cadence: Mix punchy short sentences with natural longer thoughts.

3. Content Fidelity:
   - Retain all facts, arguments, and context from the original text without losing meaning.

4. Output Format:
   - Output strictly the humanized plain text. Do not include introductory remarks, commentary, or markdown fences."""


def logMessage(messageText: str) -> None:
    # Print formatted log according to rule standard
    currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"({currentTime}) {messageText}")


def cleanOutput(rawText: str) -> str:
    # Remove markdown bold formatting
    cleanedText = re.sub(r'\*\*([^*]+)\*\*', r'\1', rawText)

    # Remove markdown italic formatting
    cleanedText = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\1', cleanedText)

    # Replace awkward Indonesian calque 'ruang/situasi di mana' with natural 'tempat' or 'saat'
    cleanedText = re.sub(r'\b(ruang|wadah|lingkungan)\s+di mana\b', r'\1 tempat', cleanedText, flags=re.IGNORECASE)
    cleanedText = re.sub(r'\b(kondisi|situasi|masa|saat)\s+di mana\b', r'\1 saat', cleanedText, flags=re.IGNORECASE)

    # Normalize multiple whitespace characters
    cleanedText = re.sub(r'[ \t]+', ' ', cleanedText)

    return cleanedText.strip()


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

    # Detect structural AI fingerprints across document
    markdownMatches = MARKDOWN_PATTERN.findall(sourceText)
    markdownCount = len(markdownMatches)
    antithesisMatches = ANTITHESIS_PATTERN.findall(sourceText)
    antithesisCount = len(antithesisMatches)
    triadMatches = TRIAD_PATTERN.findall(sourceText)
    triadCount = len(triadMatches)
    calqueMatches = CALQUE_PATTERN.findall(sourceText)
    calqueCount = len(calqueMatches)
    copulaMatches = COPULA_PATTERN.findall(sourceText)
    copulaCount = len(copulaMatches)

    # Identify flagged sentences with cliches or structural fingerprints
    detectedList = []
    flaggedSentences = []
    for sentenceItem in sentenceList:
        hasCliche = any(pattern.search(sentenceItem) for pattern in COMPILED_PATTERNS)
        hasMarkdown = bool(MARKDOWN_PATTERN.search(sentenceItem))
        hasAntithesis = bool(ANTITHESIS_PATTERN.search(sentenceItem))
        hasTriad = bool(TRIAD_PATTERN.search(sentenceItem))
        hasCalque = bool(CALQUE_PATTERN.search(sentenceItem))

        if hasCliche or hasMarkdown or hasAntithesis or hasTriad or hasCalque:
            flaggedSentences.append(sentenceItem)

        for pattern in COMPILED_PATTERNS:
            foundPatterns = pattern.findall(sentenceItem)
            if foundPatterns:
                detectedList.extend(foundPatterns)

    clicheCount = len(detectedList)

    # Calculate structural deduction penalties
    structuralPenalty = 0
    if markdownCount > 0:
        structuralPenalty += 20
    if antithesisCount > 1:
        structuralPenalty += 12
    if triadCount > 1:
        structuralPenalty += 10
    if calqueCount > 0:
        structuralPenalty += 8

    # Apply penalty for high copula density in multi-sentence texts
    copulaRatio = copulaCount / max(1, sentenceCount)
    if copulaRatio > 0.35 and sentenceCount >= 3:
        structuralPenalty += 10

    # Calculate human authenticity score
    clichePenalty = min(MAX_PENALTY, clicheCount * CLICHE_WEIGHT)
    burstinessBonus = BURST_BONUS if standardDeviation >= BURST_THRESHOLD else (-FLAT_PENALTY if standardDeviation < 3.0 and sentenceCount > 2 else 0)
    calculatedScore = max(10, min(98, BASE_SCORE - clichePenalty - structuralPenalty + burstinessBonus))

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

    # Clean draft text from markdown and structural artifacts
    draftText = cleanOutput(draftText)

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
    flaggedSample = "\n".join(f"- {sentence}" for sentence in auditMetrics["flaggedSentences"][:5])
    refineInstruction = (
        f"The following rewritten text is close, but these specific sentences still trigger AI detection patterns:\n"
        f"{flaggedSample}\n\n"
        f"Refinement requirements:\n"
        f"1. Replace static definitional 'adalah/merupakan' statements with active, dynamic verbs.\n"
        f"2. Break repetitive 'bukan ..., melainkan ...' contrasts and three-part lists into natural varied thoughts.\n"
        f"3. Strip all markdown bold or italic styling completely.\n"
        f"4. Eliminate 'di mana' relative clauses.\n"
        f"5. Maintain exact paragraph structure and length (~1:1 ratio):\n\n"
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

    # Clean refined text from markdown and structural artifacts
    finalText = cleanOutput(refinedText)

    logMessage("Adversarial refinement pass completed successfully")
    return finalText
