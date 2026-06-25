import os
import fitz  # PyMuPDF
from typing import List

def parse_document(file_path: str) -> str:
    """
    Parses unstructured files (PDF, txt, email logs) and extracts layout-aware clean text.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    _, ext = os.path.splitext(file_path.lower())
    if ext == ".pdf":
        return parse_pdf(file_path)
    else:
        # Fallback to plain text reading for emails (.eml), TXT, etc.
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

def parse_pdf(file_path: str) -> str:
    """
    Uses PyMuPDF to parse PDF text blocks, sorted by coordinate layout position
    (y-axis top-to-bottom, then x-axis left-to-right) to preserve visual order.
    """
    doc = fitz.open(file_path)
    full_text = []
    
    for page in doc:
        # Get blocks: (x0, y0, x1, y1, "text", block_no, block_type)
        blocks = page.get_text("blocks")
        
        # Sort blocks primarily by y0 (vertical position) and secondarily by x0 (horizontal position)
        sorted_blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
        
        for block in sorted_blocks:
            text = block[4].strip()
            if text:
                full_text.append(text)
                
    doc.close()
    return "\n\n".join(full_text)

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Chunks document text dynamically based on paragraphs, respecting chunk boundaries
    and keeping overlap context.
    """
    chunks = []
    if not text:
        return chunks
        
    paragraphs = text.split("\n\n")
    current_chunk = []
    current_length = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        para_len = len(para)
        
        # If adding this paragraph exceeds chunk_size, save current chunk and roll back overlap
        if current_length + para_len > chunk_size and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            
            # Form overlap: keep paragraphs from the end of current chunk up to chunk_overlap
            overlap_chunk = []
            overlap_len = 0
            for prev_para in reversed(current_chunk):
                if overlap_len + len(prev_para) < chunk_overlap:
                    overlap_chunk.insert(0, prev_para)
                    overlap_len += len(prev_para) + 2  # including paragraph separator \n\n
                else:
                    break
            current_chunk = overlap_chunk
            current_length = overlap_len
            
        current_chunk.append(para)
        current_length += para_len + 2
        
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
        
    return chunks
