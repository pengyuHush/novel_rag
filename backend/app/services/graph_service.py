"""Character relationship graph generation service."""

from __future__ import annotations

import asyncio
import json
import re
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple

import jieba
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharacterGraph, Novel
from app.repositories.character_graph_repository import CharacterGraphRepository
from app.repositories.novel_repository import NovelRepository
from app.schemas.graph import CharacterGraphResponse, CharacterNode, RelationshipEdge


class GraphService:
    """Generate and retrieve character relationship graphs."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.novel_repo = NovelRepository(session)
        self.graph_repo = CharacterGraphRepository(session)

    async def get_graph(self, novel_id: str) -> CharacterGraphResponse | None:
        graph = await self.graph_repo.get(novel_id)
        if not graph:
            return None

        characters = [CharacterNode(**ch) for ch in graph.characters]
        relationships = [RelationshipEdge(**rel) for rel in graph.relationships]
        return CharacterGraphResponse(
            novel_id=novel_id,
            characters=characters,
            relationships=relationships,
            version=graph.version,
        )

    async def generate_graph(self, novel_id: str) -> CharacterGraphResponse:
        """Generate character graph using simple NER and co-occurrence."""
        logger.info(f"Generating character graph for novel {novel_id}")
        novel = await self.novel_repo.get(novel_id)
        if not novel or not novel.content:
            raise ValueError(f"Novel {novel_id} has no content")

        # Extract characters
        characters_map = await self._extract_characters(novel.content)
        if not characters_map:
            logger.warning(f"No characters found in novel {novel_id}")
            characters_map = {"未知": {"count": 1, "positions": [0]}}

        # Extract relationships
        relationships_list = await self._extract_relationships(novel.content, list(characters_map.keys()))

        # Build schema
        characters = [
            CharacterNode(
                id=name,
                name=name,
                importance=float(min(1.0, data["count"] / 100)),
                occurrences=data["count"],
            )
            for name, data in characters_map.items()
        ]

        relationships = [
            RelationshipEdge(
                source=rel["source"],
                target=rel["target"],
                relation=rel["relation"],
                weight=rel["weight"],
                evidence=rel["evidence"][:3],  # Limit evidence
            )
            for rel in relationships_list
        ]

        # Persist
        graph_model = CharacterGraph(
            novel_id=novel_id,
            characters=[ch.model_dump() for ch in characters],
            relationships=[rel.model_dump() for rel in relationships],
            version="1.0",
        )
        await self.graph_repo.upsert(graph_model)
        await self.session.commit()

        # Mark novel as having graph
        novel.has_graph = True
        await self.session.commit()

        logger.info(f"Graph generated: {len(characters)} characters, {len(relationships)} relationships")
        return CharacterGraphResponse(
            novel_id=novel_id,
            characters=characters,
            relationships=relationships,
            version="1.0",
        )

    async def _extract_characters(self, text: str) -> Dict[str, Dict]:
        """Extract character names using simple rules."""
        # Simple Chinese name pattern (2-4 characters)
        name_pattern = re.compile(r"[\u4e00-\u9fff]{2,4}")
        paragraphs = text.split("\n")

        candidates: Counter[str] = Counter()
        positions: defaultdict[str, List[int]] = defaultdict(list)

        for idx, para in enumerate(paragraphs):
            # Use jieba to find potential names
            words = jieba.lcut(para)
            for word in words:
                if name_pattern.fullmatch(word):
                    candidates[word] += 1
                    positions[word].append(idx)

        # Filter: keep names that appear at least 5 times
        characters = {
            name: {"count": count, "positions": positions[name]}
            for name, count in candidates.items()
            if count >= 5
        }

        # Limit to top 50 characters
        sorted_chars = sorted(characters.items(), key=lambda x: x[1]["count"], reverse=True)
        return dict(sorted_chars[:50])

    async def _extract_relationships(self, text: str, character_names: List[str]) -> List[Dict]:
        """Extract relationships using co-occurrence in paragraphs."""
        paragraphs = text.split("\n\n")
        co_occurrence: Counter[Tuple[str, str]] = Counter()
        evidence_map: defaultdict[Tuple[str, str], List[str]] = defaultdict(list)

        for para in paragraphs:
            found = [name for name in character_names if name in para]
            if len(found) < 2:
                continue

            for i, name1 in enumerate(found):
                for name2 in found[i + 1 :]:
                    pair = tuple(sorted([name1, name2]))
                    co_occurrence[pair] += 1
                    if len(evidence_map[pair]) < 5:
                        evidence_map[pair].append(para[:100])

        relationships = []
        for (name1, name2), count in co_occurrence.most_common(100):
            relationships.append(
                {
                    "source": name1,
                    "target": name2,
                    "relation": "相关",
                    "weight": float(min(1.0, count / 10)),
                    "evidence": evidence_map[(name1, name2)],
                }
            )

        return relationships

    async def delete_graph(self, novel_id: str) -> None:
        """Delete character graph for a novel."""
        logger.info(f"Deleting character graph for novel {novel_id}")
        
        # Delete from database
        await self.graph_repo.delete(novel_id)
        await self.session.commit()
        
        # Update novel flag
        novel = await self.novel_repo.get(novel_id)
        if novel:
            novel.has_graph = False
            await self.session.commit()
        
        logger.info(f"Graph deleted for novel {novel_id}")


__all__ = ["GraphService"]

