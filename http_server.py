from aiohttp import web


class GetView(web.View):

    async def get(self):
        messages = self.request.app.db.get_messages()
        return web.json_response({'messages': messages})


class GetPostView(GetView):

    async def post(self):
        text = await self.request.text()
        id = self.request.app.current_message_id
        self.request.app.current_message_id += 1

        await self.request.app.db.append(msg=text, id=id)
        await self.request.app.grpc_sender.send_to_nodes(msg=text, id=id)

        return web.Response(status=201)


class GetMessagesApi(web.Application):

    def __init__(self, db, view):
        super().__init__()
        self.grpc_task = None
        self.db = db
        self.router.add_view('/', view)
