
from flask import Blueprint, render_template

# Create the blueprint object
v1_routes = Blueprint('v1_routes', __name__)
@v1_routes.route('/health')
def health_check():
    return {"status": "healthy"}