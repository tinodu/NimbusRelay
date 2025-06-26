"""
Main application entry point for NimbusRelay
Refactored to use modular architecture following SOLID principles
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from src.core.app_factory import create_app, run_app
from src.config.settings import DevelopmentConfig


def main():
    """Main application entry point"""
    try:
        # Create application using factory pattern
        app, socketio = create_app(DevelopmentConfig)
        
        # Run the application
        run_app(app, socketio)
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
