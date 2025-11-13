from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List


@dataclass
class BookmarkNode:
    title: str
    level: int
    page: int
    zoom: str | None = None
    children: List["BookmarkNode"] = field(default_factory=list)

    def to_flat(self) -> List["BookmarkNode"]:
        nodes = [self]
        for child in self.children:
            nodes.extend(child.to_flat())
        return nodes


def parse_dump(text: str) -> list[BookmarkNode]:
    """Parse pdftk dump_data_utf8 text into a tree."""
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if line == "BookmarkBegin":
            if current:
                entries.append(current)
            current = {}
            continue
        if not current:
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        current[key.strip()] = value.strip()
    if current:
        entries.append(current)
    nodes: list[BookmarkNode] = []
    stack: list[BookmarkNode] = []
    for entry in entries:
        title = entry.get("BookmarkTitle", "Untitled")
        level = int(entry.get("BookmarkLevel", "1"))
        page = int(entry.get("BookmarkPageNumber", "1"))
        zoom = entry.get("BookmarkZoom")
        node = BookmarkNode(title=title, level=level, page=page, zoom=zoom)
        while stack and stack[-1].level >= level:
            stack.pop()
        if stack:
            stack[-1].children.append(node)
        else:
            nodes.append(node)
        stack.append(node)
    return nodes


def serialize_nodes(nodes: Iterable[BookmarkNode]) -> str:
    """Serialize nodes into pdftk dump_data_utf8 format."""
    lines: list[str] = []
    for node in nodes:
        lines.extend(_serialize_node(node))
    return "\n".join(lines) + ("\n" if lines else "")


def _serialize_node(node: BookmarkNode) -> list[str]:
    lines = [
        "BookmarkBegin",
        f"BookmarkTitle: {node.title}",
        f"BookmarkLevel: {node.level}",
        f"BookmarkPageNumber: {node.page}",
    ]
    if node.zoom:
        lines.append(f"BookmarkZoom: {node.zoom}")
    for child in node.children:
        lines.extend(_serialize_node(child))
    return lines
