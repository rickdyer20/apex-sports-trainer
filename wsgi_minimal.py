#!/usr/bin/env python3
"""
MINIMAL WSGI - Diagnostic Test
=============================
"""

from diagnostic import app as application

if __name__ == "__main__":
    application.run()
