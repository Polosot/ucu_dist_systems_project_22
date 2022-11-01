import asyncio


class Storage:

    def __init__(self, logger, delay=0.0):
        self.logger = logger
        self.delay = delay
        self.data = dict()

    async def append(self, msg, id):
        self.logger.info(f'Appending message {msg}, id {id}')

        if self.delay:
            self.logger.info('delay')
            await asyncio.sleep(self.delay)

        self.data[id] = msg
        self.logger.info('message appended')

    def get_messages(self):
        self.logger.info('get list')
        return [msg for _, msg in sorted(self.data.items(), key=lambda x: x[0])]
