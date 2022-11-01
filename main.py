import argparse
import asyncio
import logging
import sys

from aiohttp import web

from db.storage import Storage
from grpc_conn.grpc_connect import GrpcReceiver
from grpc_conn.grpc_connect import GrpcSender
from http_server import GetPostView, GetMessagesApi
from http_server import GetView


class SecondaryApp(GetMessagesApi):

    def __init__(self, db):
        super().__init__(db, GetView)


class MasterApp(GetMessagesApi):
    def __init__(self, db, nodes):

        super().__init__(db, GetPostView)
        self.current_message_id = 0
        self.grpc_sender = GrpcSender(nodes)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--is_master', help='Master node', required=False, action='store_true')
    parser.add_argument('--http_port', help='Port for the Http Api', required=True, type=int)
    parser.add_argument('--grpc_port', help='Port for GRPC', required=False, type=int)
    parser.add_argument('--delay', help='Delay, sec', required=False, default=0.0, type=float)
    parser.add_argument('--secondary_nodes', '-sn', help='List of host:port ', nargs='*')

    args = parser.parse_args()

    assert args.is_master == (not bool(args.grpc_port)), "`grpc_port` parameter shouldn't be set for the master node"
    assert args.is_master == bool(args.secondary_nodes), \
        "`secondary_nodes` parameter shouldn't be set for the secondary node"

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    db = Storage(logger=logger, delay=args.delay)

    if args.is_master:
        app = MasterApp(db, nodes=args.secondary_nodes)
        web.run_app(app, port=args.http_port)
    else:
        app = SecondaryApp(db)
        new_event_loop = asyncio.new_event_loop()
        grpc_receiver = GrpcReceiver(db=db, port=args.grpc_port)
        new_event_loop.create_task(grpc_receiver.start())
        app.on_shutdown.append(grpc_receiver.stop)
        web.run_app(app, port=args.http_port, loop=new_event_loop)
        new_event_loop.close()
