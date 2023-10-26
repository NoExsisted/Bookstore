from be.view import auth, search
from be.view import seller
from be.view import buyer
from be.model.store import init_database
from flask import Flask


# bp_shutdown = Blueprint("shutdown", __name__)


# def shutdown_server():
#     func = request.environ.get("werkzeug.server.shutdown")
#     if func is None:
#         raise RuntimeError("Not running with the Werkzeug Server")
#     func()
#
#
# @bp_shutdown.route("/shutdown")
# def be_shutdown():
#     shutdown_server()
#     return "Server shutting down..."


def be_run():
    app = Flask(__name__)


    # this_path = os.path.dirname(__file__)
    # parent_path = os.path.dirname(this_path)
    # log_file = os.path.join(parent_path, "app.log")

    init_database('127.0.0.1', 27017, 'bookstore')
    # logging.basicConfig(filename=log_file, level=logging.ERROR)
    # handler = logging.StreamHandler()
    # formatter = logging.Formatter(
    #     "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    # )
    # handler.setFormatter(formatter)
    # logging.getLogger().addHandler(handler)

    # app.register_blueprint(bp_shutdown)
    app.register_blueprint(auth.bp_auth)
    # app.register_blueprint(search.bp_search)
    app.register_blueprint(seller.bp_seller)
    app.register_blueprint(buyer.bp_buyer)

    app.run(host='127.0.0.1', port=5000)
