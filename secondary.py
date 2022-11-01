from http_server import GetView, GetMessagesApi
import argparse
from aiohttp import web
from db.storage import Storage
import logging
from grpc_conn.grpc_connect import GrpcReceiver
import asyncio
import sys


class SecondaryApp(GetMessagesApi):

    def __init__(self, db):
        super().__init__(db, GetView)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--http_port', help='Port for the Http Api', required=True, type=int)
    parser.add_argument('--grpc_port', help='Port for GRPC', required=True, type=int)
    parser.add_argument('--delay', help='Delay, sec', required=False, default=0.0, type=float)
    args = parser.parse_args()

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    db = Storage(logger=logger, delay=args.delay)
    grpc_receiver = GrpcReceiver(db=db, port=args.grpc_port)

    new_event_loop = asyncio.new_event_loop()
    new_event_loop.create_task(grpc_receiver.start())

    app = SecondaryApp(db)
    app.on_shutdown.append(grpc_receiver.stop)
    web.run_app(app, port=args.http_port, loop=new_event_loop)

    new_event_loop.close()