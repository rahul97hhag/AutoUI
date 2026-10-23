from flask import jsonify


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(err):
        return jsonify(error="bad_request", message=str(err)), 400

    @app.errorhandler(404)
    def not_found(err):
        return jsonify(error="not_found", message=str(err)), 404

    @app.errorhandler(405)
    def method_not_allowed(err):
        return jsonify(error="method_not_allowed", message=str(err)), 405

    @app.errorhandler(500)
    def internal_error(err):
        return jsonify(error="internal_server_error", message=str(err)), 500
