from typing import List, Dict, Any
import collections
import os
from ..api.schemas import ProjectStructure

def analyze_project_structure(tree: List[Dict[str, Any]]) -> ProjectStructure:
    """
    Analyzes the repository file tree to understand project composition.
    Categorizes files by extension and identifies core folders.
    """
    extension_counts = collections.defaultdict(int)
    folder_counts = collections.defaultdict(int)
    total_files = 0
    
    # Common mappings for grouping
    # For now, we'll keep raw extensions but clean them up
    
    for item in tree:
        if item.get("type") == "blob": # It's a file
            total_files += 1
            path = item.get("path", "")
            
            # Get extension
            _, ext = os.path.splitext(path)
            if ext:
                extension_counts[ext.lower()] += 1
            else:
                extension_counts["no_extension"] += 1
                
        elif item.get("type") == "tree": # It's a folder
            path = item.get("path", "")
            # Only count top-level or second-level folders to avoid noise
            if "/" not in path:
                folder_counts[path] += 1

    # Documentation Status Heuristic
    doc_extensions = {".md", ".txt", ".rst", ".pdf", ".html"}
    doc_count = sum(count for ext, count in extension_counts.items() if ext in doc_extensions)
    
    doc_status = "fair"
    if total_files > 0:
        doc_ratio = doc_count / total_files
        if doc_ratio > 0.1 or doc_count > 10:
            doc_status = "excellent"
        elif doc_ratio > 0.05 or doc_count > 5:
            doc_status = "good"
        elif doc_count > 2:
            doc_status = "fair"
        else:
            doc_status = "poor"

    return ProjectStructure(
        extension_counts=dict(extension_counts),
        total_files=total_files,
        folder_counts=dict(folder_counts),
        documentation_status=doc_status
    )
