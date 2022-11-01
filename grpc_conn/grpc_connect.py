# https://medium.com/swlh/running-an-http-grpc-python-server-concurrently-on-aws-elastic-beanstalk-8524d15030e5
import grpc
from grpc_conn import message_replicator_pb2, message_replicator_pb2_grpc
from grpc.experimental.aio import init_grpc_aio
import asyncio


class GrpcSender:

    def __init__(self, nodes, logger):
        self.nodes = nodes
        self.logger = logger

    async def send(self, msg, id, node):
        async with grpc.aio.insecure_channel(node) as channel:
            stub = message_replicator_pb2_grpc.MessageReplicatorStub(channel)
            response = await stub.Replicate(message_replicator_pb2.Message(msg=msg, id=id))
            return response

    async def send_to_nodes(self, msg, id):

        self.logger.info('Sending requests to nodes via GRPC')

        tasks = asyncio.gather(*[self.send(msg, id, n) for n in self.nodes])
        results = await asyncio.ensure_future(tasks)

        return all(results)


class Replicator(message_replicator_pb2_grpc.MessageReplicatorServicer):

    def __init__(self, db, logger):
        self.db = db
        self.logger = logger

    async def Replicate(self, request, context):

        self.logger.info('Incoming GRPC request')
        await self.db.append(msg=request.msg, id=request.id)
        return message_replicator_pb2.Ack(success=True)


class GrpcReceiver:

    def __init__(self, db, logger, port):
        self.db = db
        self.port = port
        self.logger = logger
        self.server = None

    async def start(self, *args, **kwargs):

        init_grpc_aio()
        self.server = grpc.aio.server()
        message_replicator_pb2_grpc.add_MessageReplicatorServicer_to_server(Replicator(self.db, self.logger),
                                                                            self.server)
        self.server.add_insecure_port('[::]:' + str(self.port))
        self.logger.info("GRPC server started, listening on " + str(self.port))
        await self.server.start()
        await self.server.wait_for_termination()

    async def stop(self, *args, **kwargs):
        self.logger.info('Stopping GRPC server')
        await self.server.stop(0)
        await self.server.wait_for_termination()
