import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.app import app

if __name__ == '__main__':
    app.run(debug=True)