#!/usr/bin/env python
"""
Executable for the Ceryx server.
"""

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/opt/ceryx')

    from ceryx import settings
    from ceryx.manager import app
    app.run(host=settings.WEB_BIND_HOST, port=settings.WEB_BIND_PORT)
