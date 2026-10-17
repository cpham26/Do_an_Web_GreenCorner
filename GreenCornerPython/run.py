import os
import sys

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app import create_app
from db_init import init_db

app = create_app()

if __name__ == '__main__':
    # Initialize database and default seed data if needed
    init_db(app)

    port = int(os.environ.get('PORT', 5000))
    print("==========================================================")
    print("Green Corner Python Web Server is running!")
    print(f"Storefront URL : http://127.0.0.1:{port}")
    print("==========================================================")
    app.run(host='0.0.0.0', port=port, debug=False)
