
from grpc_conn.grpc_connect import GrpcSender
from http_server import GetPostView, GetMessagesApi
import argparse
from aiohttp import web
from db.storage import Storage
import logging
import sys


class MasterApp(GetMessagesApi):
    def __init__(self, db, nodes):

        super().__init__(db, GetPostView)
        self.current_message_id = 0
        self.grpc_sender = GrpcSender(nodes)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--http_port', help='Port for the Http Api', required=True, type=int)
    parser.add_argument('--secondary_node', '-n', nargs='*')
    args = parser.parse_args()

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logger.info('Master has started')
    db = Storage(logger=logger)
    app = MasterApp(db, nodes=args.secondary_node)
    web.run_app(app, port=args.http_port)