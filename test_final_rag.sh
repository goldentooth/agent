#!/bin/bash

echo "🚀 Testing Final RAG System"
echo "=========================="

echo ""
echo "📝 Query 1: Single message test"
echo "What repositories are available?" | goldentooth-agent send --agent rag

echo ""
echo "📝 Query 2: Testing confidence and sources"
echo "Tell me about Python programming" | goldentooth-agent send --agent rag --format json | jq '.metadata.sources, .metadata.confidence'

echo ""
echo "📝 Query 3: Complex query"
echo "What infrastructure tools are used in the terraform repositories?" | goldentooth-agent send --agent rag

echo ""
echo "✅ Final RAG test completed!"