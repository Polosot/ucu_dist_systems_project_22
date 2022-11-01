from aiohttp import web


class GetView(web.View):

    async def get(self):
        self.request.app.logger.info('GET request')
        messages = self.request.app.db.get_messages()
        return web.json_response({'messages': messages})


class GetPostView(GetView):

    async def post(self):
        text = await self.request.text()
        id = self.request.app.current_message_id
        self.request.app.current_message_id += 1

        self.request.app.logger.info(f'POST request, message: {text}')

        await self.request.app.db.append(msg=text, id=id)
        success = await self.request.app.grpc_sender.send_to_nodes(msg=text, id=id)

        if success:
            self.request.app.logger.info(f'Message {text} has successfully added to nodes')
            return web.Response(status=201)
        else:
            self.request.app.logger.info(f'Error during adding the message {text} to nodes')
            return web.Response(status=500)


class GetMessagesApi(web.Application):

    def __init__(self, db, logger, view):
        super().__init__()
        self.grpc_task = None
        self.db = db
        self.logger = logger
        self.router.add_view('/', view)
        self.logger.info('Application has started')
