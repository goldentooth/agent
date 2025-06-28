"""AI-powered tools for text processing, analysis, and content generation."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from pydantic import Field

from ..flow_agent import FlowIOSchema, FlowTool


# Text Analysis Tool
class TextAnalysisInput(FlowIOSchema):
    """Input schema for text analysis tool."""

    text: str = Field(..., description="Text to analyze")
    include_sentiment: bool = Field(
        default=True, description="Include sentiment analysis"
    )
    include_keywords: bool = Field(default=True, description="Extract keywords")
    include_stats: bool = Field(default=True, description="Include text statistics")
    include_readability: bool = Field(
        default=True, description="Include readability metrics"
    )
    keyword_count: int = Field(
        default=10, description="Number of top keywords to extract"
    )


class TextAnalysisOutput(FlowIOSchema):
    """Output schema for text analysis tool."""

    text_length: int = Field(..., description="Length of input text")
    word_count: int = Field(..., description="Number of words")
    sentence_count: int = Field(..., description="Number of sentences")
    paragraph_count: int = Field(..., description="Number of paragraphs")
    keywords: list[str] = Field(default_factory=list, description="Extracted keywords")
    sentiment_score: float | None = Field(
        default=None, description="Sentiment score (-1 to 1)"
    )
    sentiment_label: str | None = Field(default=None, description="Sentiment label")
    readability_score: float | None = Field(
        default=None, description="Readability score"
    )
    language_detected: str | None = Field(default=None, description="Detected language")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional analysis data"
    )
    success: bool = Field(..., description="Whether analysis was successful")
    error: str | None = Field(default=None, description="Error message if failed")


async def text_analysis_implementation(
    input_data: TextAnalysisInput,
) -> TextAnalysisOutput:
    """Analyze text content with statistics, keywords, and sentiment."""
    try:
        text = input_data.text.strip()

        if not text:
            return TextAnalysisOutput(
                text_length=0,
                word_count=0,
                sentence_count=0,
                paragraph_count=0,
                success=False,
                error="Empty text provided",
            )

        # Basic text statistics
        text_length = len(text)
        words = re.findall(r"\b\w+\b", text.lower())
        word_count = len(words)

        # Count sentences (simple approach)
        sentences = re.split(r"[.!?]+", text)
        sentence_count = len([s for s in sentences if s.strip()])

        # Count paragraphs
        paragraphs = text.split("\n\n")
        paragraph_count = len([p for p in paragraphs if p.strip()])

        # Extract keywords if requested
        keywords = []
        if input_data.include_keywords and words:
            # Simple keyword extraction: most common words (excluding stop words)
            stop_words = {
                "the",
                "a",
                "an",
                "and",
                "or",
                "but",
                "in",
                "on",
                "at",
                "to",
                "for",
                "of",
                "with",
                "by",
                "is",
                "are",
                "was",
                "were",
                "be",
                "been",
                "being",
                "have",
                "has",
                "had",
                "do",
                "does",
                "did",
                "will",
                "would",
                "could",
                "should",
                "may",
                "might",
                "must",
                "can",
                "this",
                "that",
                "these",
                "those",
                "i",
                "you",
                "he",
                "she",
                "it",
                "we",
                "they",
                "me",
                "him",
                "her",
                "us",
                "them",
                "my",
                "your",
                "his",
                "its",
                "our",
                "their",
            }

            filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
            word_freq = Counter(filtered_words)
            keywords = [
                word for word, _ in word_freq.most_common(input_data.keyword_count)
            ]

        # Simple sentiment analysis (basic approach)
        sentiment_score = None
        sentiment_label = None
        if input_data.include_sentiment:
            positive_words = {
                "good",
                "great",
                "excellent",
                "amazing",
                "wonderful",
                "fantastic",
                "love",
                "like",
                "enjoy",
                "happy",
                "pleased",
                "satisfied",
                "positive",
                "awesome",
                "brilliant",
                "perfect",
                "beautiful",
                "best",
                "better",
            }
            negative_words = {
                "bad",
                "terrible",
                "awful",
                "horrible",
                "hate",
                "dislike",
                "angry",
                "sad",
                "disappointed",
                "frustrated",
                "annoyed",
                "worst",
                "worse",
                "negative",
                "problem",
                "issue",
                "error",
                "fail",
                "wrong",
                "poor",
            }

            pos_count = sum(1 for word in words if word in positive_words)
            neg_count = sum(1 for word in words if word in negative_words)

            total_sentiment_words = pos_count + neg_count
            if total_sentiment_words > 0:
                sentiment_score = (pos_count - neg_count) / total_sentiment_words
                if sentiment_score > 0.1:
                    sentiment_label = "positive"
                elif sentiment_score < -0.1:
                    sentiment_label = "negative"
                else:
                    sentiment_label = "neutral"
            else:
                sentiment_score = 0.0
                sentiment_label = "neutral"

        # Simple readability score (Flesch-like approximation)
        readability_score = None
        if input_data.include_readability and sentence_count > 0 and word_count > 0:
            avg_sentence_length = word_count / sentence_count
            # Simple syllable estimation: count vowel groups
            syllable_count = 0
            for word in words:
                syllables = len(re.findall(r"[aeiouy]+", word))
                syllable_count += max(1, syllables)  # At least 1 syllable per word

            avg_syllables_per_word = syllable_count / word_count

            # Simplified Flesch Reading Ease approximation
            readability_score = (
                206.835
                - (1.015 * avg_sentence_length)
                - (84.6 * avg_syllables_per_word)
            )
            readability_score = max(0, min(100, readability_score))  # Clamp to 0-100

        # Language detection (very basic)
        language_detected = "en"  # Default to English for this simple implementation

        # Additional metadata
        metadata = {
            "avg_word_length": (
                sum(len(word) for word in words) / len(words) if words else 0
            ),
            "unique_words": len(set(words)),
            "vocabulary_richness": len(set(words)) / len(words) if words else 0,
            "most_common_word": words[0] if words else None,
        }

        return TextAnalysisOutput(
            text_length=text_length,
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            keywords=keywords,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            readability_score=readability_score,
            language_detected=language_detected,
            metadata=metadata,
            success=True,
            error=None,
        )

    except Exception as e:
        return TextAnalysisOutput(
            text_length=0,
            word_count=0,
            sentence_count=0,
            paragraph_count=0,
            success=False,
            error=str(e),
        )


# Text Summary Tool
class TextSummaryInput(FlowIOSchema):
    """Input schema for text summarization tool."""

    text: str = Field(..., description="Text to summarize")
    summary_type: str = Field(
        default="extractive", description="Summary type: extractive, bullet_points"
    )
    max_sentences: int = Field(default=3, description="Maximum sentences in summary")
    min_sentence_length: int = Field(
        default=10, description="Minimum sentence length to include"
    )
    preserve_order: bool = Field(
        default=True, description="Preserve original sentence order"
    )


class TextSummaryOutput(FlowIOSchema):
    """Output schema for text summarization tool."""

    original_length: int = Field(..., description="Original text length")
    summary: str = Field(..., description="Generated summary")
    summary_length: int = Field(..., description="Summary text length")
    compression_ratio: float = Field(..., description="Compression ratio (0-1)")
    sentences_used: int = Field(..., description="Number of sentences in summary")
    key_phrases: list[str] = Field(
        default_factory=list, description="Key phrases from summary"
    )
    success: bool = Field(..., description="Whether summarization was successful")
    error: str | None = Field(default=None, description="Error message if failed")


async def text_summary_implementation(
    input_data: TextSummaryInput,
) -> TextSummaryOutput:
    """Generate text summaries using extractive techniques."""
    try:
        text = input_data.text.strip()

        if not text:
            return TextSummaryOutput(
                original_length=0,
                summary="",
                summary_length=0,
                compression_ratio=0.0,
                sentences_used=0,
                success=False,
                error="Empty text provided",
            )

        original_length = len(text)

        # Split into sentences
        sentence_endings = re.compile(r"[.!?]+")
        sentences = sentence_endings.split(text)
        sentences = [
            s.strip()
            for s in sentences
            if len(s.strip()) >= input_data.min_sentence_length
        ]

        if not sentences:
            return TextSummaryOutput(
                original_length=original_length,
                summary="",
                summary_length=0,
                compression_ratio=0.0,
                sentences_used=0,
                success=False,
                error="No sentences found meeting minimum length requirement",
            )

        # Initialize variables for scope
        summary_sentences: list[str] = []
        selected_bullet_sentences: list[str] = []

        # Simple extractive summarization
        if input_data.summary_type == "extractive":
            # Score sentences based on word frequency and position
            words = re.findall(r"\b\w+\b", text.lower())
            word_freq = Counter(words)

            sentence_scores = []
            for i, sentence in enumerate(sentences):
                sentence_words = re.findall(r"\b\w+\b", sentence.lower())
                if not sentence_words:
                    continue

                # Score based on word frequency
                word_score = sum(word_freq.get(word, 0) for word in sentence_words)
                avg_word_score = word_score / len(sentence_words)

                # Boost score for earlier sentences (position bias)
                position_score = 1.0 / (i + 1) if i < 3 else 0.5

                # Length penalty for very short or very long sentences
                length_penalty = min(1.0, len(sentence) / 100) * min(
                    1.0, 200 / len(sentence)
                )

                total_score = avg_word_score * position_score * length_penalty
                sentence_scores.append((total_score, i, sentence))

            # Select top sentences
            sentence_scores.sort(reverse=True)
            selected_sentences = sentence_scores[: input_data.max_sentences]

            # Preserve original order if requested
            if input_data.preserve_order:
                selected_sentences.sort(key=lambda x: x[1])

            summary_sentences = [sentence for _, _, sentence in selected_sentences]
            summary = ". ".join(summary_sentences)
            if summary and not summary.endswith("."):
                summary += "."

        elif input_data.summary_type == "bullet_points":
            # Create bullet point summary
            sentence_scores: list[tuple[float, str]] = []
            for sentence in sentences:
                sentence_words = re.findall(r"\b\w+\b", sentence.lower())
                if len(sentence_words) < 3:  # Skip very short sentences
                    continue

                # Simple scoring based on length and word diversity
                score = (
                    len(set(sentence_words)) / len(sentence_words)
                    if sentence_words
                    else 0
                )
                sentence_scores.append((score, sentence))

            sentence_scores.sort(reverse=True)
            selected_bullet_sentences = [
                sentence for _, sentence in sentence_scores[: input_data.max_sentences]
            ]

            summary = "\n".join(
                f"• {sentence.strip()}" for sentence in selected_bullet_sentences
            )

        else:
            return TextSummaryOutput(
                original_length=original_length,
                summary="",
                summary_length=0,
                compression_ratio=0.0,
                sentences_used=0,
                success=False,
                error=f"Unknown summary type: {input_data.summary_type}",
            )

        summary_length = len(summary)
        compression_ratio = (
            summary_length / original_length if original_length > 0 else 0.0
        )
        sentences_used = (
            len(summary_sentences)
            if input_data.summary_type == "extractive"
            else len(selected_bullet_sentences)
        )

        # Extract key phrases from summary
        summary_words = re.findall(r"\b\w+\b", summary.lower())
        word_freq = Counter(summary_words)
        key_phrases = [
            word
            for word, freq in word_freq.most_common(5)
            if freq > 1 and len(word) > 3
        ]

        return TextSummaryOutput(
            original_length=original_length,
            summary=summary,
            summary_length=summary_length,
            compression_ratio=compression_ratio,
            sentences_used=sentences_used,
            key_phrases=key_phrases,
            success=True,
            error=None,
        )

    except Exception as e:
        return TextSummaryOutput(
            original_length=len(input_data.text),
            summary="",
            summary_length=0,
            compression_ratio=0.0,
            sentences_used=0,
            success=False,
            error=str(e),
        )


# Tool instances
TextAnalysisTool = FlowTool(
    name="text_analysis",
    input_schema=TextAnalysisInput,
    output_schema=TextAnalysisOutput,
    implementation=text_analysis_implementation,
    description="Analyze text with statistics, keyword extraction, sentiment analysis, and readability metrics",
)

TextSummaryTool = FlowTool(
    name="text_summary",
    input_schema=TextSummaryInput,
    output_schema=TextSummaryOutput,
    implementation=text_summary_implementation,
    description="Generate extractive text summaries with configurable length and format options",
)
