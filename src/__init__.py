import os
from flask import Flask
from src.config import Config
from src.models import db
from src.routes import init_routes
from prometheus_flask_exporter import PrometheusMetrics

def create_app():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, 'templates')
    
    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    metrics = PrometheusMetrics(app)
    try:
        metrics.info('app_info', 'Todo App', version='1.0.0')
    except ValueError:
        pass
    
    init_routes(app)
    return app
