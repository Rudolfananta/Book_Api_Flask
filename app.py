from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from flasgger import Swagger
from api import api  # now works cleanly
from api.book.endpoint import book_endpoint
from api.database.db_endpoint import database_endpoints
from api.auth.endpoints import auth_endpoint
from api.data_protected.endpoints import protected_data_endpoint
import os

load_dotenv()

app = Flask(__name__)
CORS(app)
Swagger(app)

# JWT Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(book_endpoint, url_prefix='/api/book')
app.register_blueprint(database_endpoints, url_prefix='/database')
app.register_blueprint(auth_endpoint, url_prefix='/auth')
app.register_blueprint(protected_data_endpoint, url_prefix='/protected')

@app.route('/')
def home():
    return {"message": "(*) The API is Running"}, 200

@app.route('/uploads/<path:filename>')
def serve_book_file(filename):
    """Serve book files from the upload directory."""
    return send_from_directory('uploads', filename)

if __name__ == '__main__':
    app.run(debug=True)