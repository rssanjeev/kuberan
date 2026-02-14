"""
PDF Extraction Utilities

Pure functions for extracting text, tables, and structured data from PDF documents.
Supports multiple extraction methods with fallback strategies.
"""
from typing import Dict, List, Optional, Any
import pdfplumber
import PyPDF2
from pathlib import Path


def extract_text_pdfplumber(pdf_path: str) -> str:
    """
    Extract raw text from PDF using pdfplumber (best for structured documents).
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as string
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: If extraction fails
    """
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    try:
        text_content = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        return "\n\n".join(text_content)
    except Exception as e:
        raise Exception(f"Failed to extract text with pdfplumber: {str(e)}")


def extract_text_pypdf2(pdf_path: str) -> str:
    """
    Extract raw text from PDF using PyPDF2 (fallback method).
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as string
    """
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    try:
        text_content = []
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        return "\n\n".join(text_content)
    except Exception as e:
        raise Exception(f"Failed to extract text with PyPDF2: {str(e)}")


def extract_text(pdf_path: str, method: str = "pdfplumber") -> str:
    """
    Extract text from PDF with automatic fallback.
    
    Args:
        pdf_path: Path to the PDF file
        method: Extraction method ("pdfplumber" or "pypdf2")
        
    Returns:
        Extracted text as string
    """
    try:
        if method == "pdfplumber":
            return extract_text_pdfplumber(pdf_path)
        elif method == "pypdf2":
            return extract_text_pypdf2(pdf_path)
        else:
            # Try pdfplumber first, fallback to PyPDF2
            try:
                return extract_text_pdfplumber(pdf_path)
            except Exception:
                return extract_text_pypdf2(pdf_path)
    except Exception as e:
        raise Exception(f"All extraction methods failed: {str(e)}")


def extract_tables(pdf_path: str) -> List[List[List[str]]]:
    """
    Extract all tables from PDF (one list per page).
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of pages, each containing list of tables, each table is list of rows
        Example: [[[row1, row2], [row1, row2]], [[row1, row2]]]
    """
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    all_tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    all_tables.append(page_tables)
    except Exception as e:
        raise Exception(f"Failed to extract tables: {str(e)}")
    
    return all_tables


def get_pdf_metadata(pdf_path: str) -> Dict[str, Any]:
    """
    Extract PDF metadata (author, creation date, etc.).
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary with metadata fields
    """
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            metadata = pdf_reader.metadata
            
            return {
                "title": metadata.get("/Title", ""),
                "author": metadata.get("/Author", ""),
                "subject": metadata.get("/Subject", ""),
                "creator": metadata.get("/Creator", ""),
                "producer": metadata.get("/Producer", ""),
                "creation_date": metadata.get("/CreationDate", ""),
                "modification_date": metadata.get("/ModDate", ""),
                "num_pages": len(pdf_reader.pages)
            }
    except Exception as e:
        return {"error": str(e), "num_pages": 0}


def extract_structured_data(pdf_path: str) -> Dict[str, Any]:
    """
    Extract comprehensive structured data from PDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary containing text, tables, and metadata
    """
    return {
        "text": extract_text(pdf_path),
        "tables": extract_tables(pdf_path),
        "metadata": get_pdf_metadata(pdf_path)
    }
