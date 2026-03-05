# summarization/__init__.py
from .dual_summarizer import (
    dual_summarization, 
    abstractive_summary, 
    extractive_summary,
    generate_abstractive_summary,
    generate_extractive_summary
)
from .chapter_generator import (
    generate_chapters,
    generate_chapters_from_topics,  # Add this
    format_chapter_markdown,
    generate_chapter_timeline
)
from .speaker_summarizer import (
    generate_speaker_summaries,
    format_speaker_summaries,
    get_speaker_statistics
)

__all__ = [
    'dual_summarization',
    'abstractive_summary',
    'extractive_summary',
    'generate_abstractive_summary',
    'generate_extractive_summary',
    'generate_chapters',
    'generate_chapters_from_topics',  # Add this
    'format_chapter_markdown',
    'generate_chapter_timeline',
    'generate_speaker_summaries',
    'format_speaker_summaries',
    'get_speaker_statistics'
]