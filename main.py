import os
from app import create_app
from app.config import create_context_processor

app = create_app()

# Initialize URL configuration context processor
url_config = create_context_processor(app)

def entry_point(request):
    return app

# functions-framework --target=entry_point --debug

if __name__ == '__main__':
    # Get Flask configuration from environment variables
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    # Run the Flask app with configuration from .env
    app.run(debug=debug_mode, host=host, port=port)