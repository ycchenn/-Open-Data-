from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .extensions import init_services


def create_app(config_object: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.json.sort_keys = False  # 保留產銷履歷表格欄位順序
    CORS(app, origins=app.config["CORS_ORIGINS"])

    init_services(app)

    from .routes.health import bp as health_bp
    from .routes.speech import bp as speech_bp
    from .routes.logs import bp as logs_bp
    from .routes.traceability import bp as traceability_bp
    from .routes.marketing import bp as marketing_bp
    from .routes.qa import bp as qa_bp

    for bp in (health_bp, speech_bp, logs_bp, traceability_bp, marketing_bp, qa_bp):
        app.register_blueprint(bp, url_prefix="/api")

    @app.errorhandler(ValueError)
    def handle_value_error(err):
        return jsonify({"error": str(err)}), 400

    return app
