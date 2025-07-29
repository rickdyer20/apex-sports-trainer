#!/usr/bin/env python3
"""
Clean WSGI Entry Point - Diagnostic Test
========================================

Simple, single-purpose WSGI file to test fundamental deployment.
No complex imports, no fallback chains, no dependencies beyond Flask.
"""

from diagnostic import app as application

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port)
