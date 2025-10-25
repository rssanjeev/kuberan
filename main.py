#!/usr/bin/env python3
"""
Investment Projection Tool - Main Entry Point

This is the main entry point that uses the new object-oriented architecture.
The actual application logic is now organized into proper models and services.
"""

import asyncio
from app import main

if __name__ == "__main__":
    asyncio.run(main())