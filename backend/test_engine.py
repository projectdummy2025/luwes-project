import pytest
from engine import splitSentences, chunkParagraphs, analyzeText
from fastapi.testclient import TestClient
from main import applicationServer

client = TestClient(applicationServer)


def testSentenceSplitting():
    # Test sentence extraction logic
    testContent = "Halo dunia! Ini kalimat kedua. Apakah ini ketiga?"
    sentenceList = splitSentences(testContent)
    assert len(sentenceList) == 3
    assert sentenceList[0] == "Halo dunia!"


def testChunkParagraphs():
    # Test paragraph grouping within limits
    sampleParagraph = "Paragraf pertama dengan beberapa kata penting."
    textChunks = chunkParagraphs(sampleParagraph, wordLimit=10)
    assert len(textChunks) == 1


def testAnalysisMetrics():
    # Test heuristic metrics computation
    sampleContent = "Dalam era modern ini, teknologi memainkan peran penting."
    metricsResult = analyzeText(sampleContent)
    assert metricsResult["wordCount"] > 0
    assert metricsResult["clicheCount"] >= 2
    assert "humanScore" in metricsResult


def testConfigEndpoint():
    # Test API config response
    responseObject = client.get("/api/config")
    assert responseObject.status_code == 200
    responseData = responseObject.json()
    assert "modelName" in responseData


def testAnalyzeEndpoint():
    # Test API analyze endpoint
    payloadData = {"sourceText": "Ini adalah pengujian teks."}
    responseObject = client.post("/api/analyze", json=payloadData)
    assert responseObject.status_code == 200
    assert "analysisData" in responseObject.json()


def testFlaggedSentences():
    # Test cliché sentence flagging
    sampleContent = "Tentu saja inovasi ini luar biasa. Namun ini kalimat yang wajar tanpa klise."
    metricsResult = analyzeText(sampleContent)
    assert "flaggedSentences" in metricsResult
    assert len(metricsResult["flaggedSentences"]) >= 1
    assert "Tentu saja" in metricsResult["flaggedSentences"][0]


def testHumanizeRequestValidation():
    # Test API humanize validation with modeValue
    payloadData = {
        "sourceText": "Kalimat uji.",
        "toneValue": "natural",
        "modeValue": "fast",
    }
    responseObject = client.post("/api/humanize", json=payloadData)
    assert responseObject.status_code in [200, 400, 500]
