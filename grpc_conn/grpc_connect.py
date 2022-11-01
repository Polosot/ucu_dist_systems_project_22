# https://medium.com/swlh/running-an-http-grpc-python-server-concurrently-on-aws-elastic-beanstalk-8524d15030e5
import grpc
from grpc_conn import message_replicator_pb2, message_replicator_pb2_grpc
from grpc.experimental.aio import init_grpc_aio
import asyncio


class GrpcSender:

    def __init__(self, nodes):
        self.nodes = nodes

    async def send(self, msg, id, node):
        async with grpc.aio.insecure_channel(node) as channel:
            stub = message_replicator_pb2_grpc.MessageReplicatorStub(channel)
            response = await stub.Replicate(message_replicator_pb2.Message(msg=msg, id=id))
            return response

    async def send_to_nodes(self, msg, id):

        tasks = asyncio.gather(*[self.send(msg, id, n) for n in self.nodes])
        results = await asyncio.ensure_future(tasks)

        return all(results)


class Replicator(message_replicator_pb2_grpc.MessageReplicatorServicer):

    def __init__(self, db):

        self.db = db

    async def Replicate(self, request, context):

        print('replicateeeeee')

        await self.db.append(msg=request.msg, id=request.id)
        return message_replicator_pb2.Ack(success=True)


class GrpcReceiver:

    def __init__(self, db, port):
        self.db = db
        self.port = port
        self.server = None

    async def start(self, *args, **kwargs):

        init_grpc_aio()
        self.server = grpc.aio.server()
        message_replicator_pb2_grpc.add_MessageReplicatorServicer_to_server(Replicator(self.db), self.server)
        self.server.add_insecure_port('[::]:' + str(self.port))
        print("Server started, listening on " + str(self.port))
        await self.server.start()
        await self.server.wait_for_termination()

    async def stop(self, *args, **kwargs):
        print('stoppp')
        await self.server.stop(0)
        await self.server.wait_for_termination()
