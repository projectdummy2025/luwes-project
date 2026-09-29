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
