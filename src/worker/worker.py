import json
import asyncio
import aioredis

QUEUES = [
    'queue:high',
    'queue:medium',
    'queue:low'
]

async def work(raw_data):
    """
    Do job, data shape:
    {
        'id': UUID of job,
        'content': JSON object to use in template
        OR
        'html': HTML to generate pdf for
    }
    :param raw_data: json bytes
    :return:
    """
    text = raw_data.decode('utf8')
    data = json.loads(text)
    print('data', data)
    # TODO update job status in pg
    # TODO generate html
    # TODO update pg with html
    # TODO optionally download any required files asynchronously, requires squid
    # TODO generate PDF, maybe use run_in_executor and BoundedSemaphore to allow two of these to happen
    # TODO update job status in pg
    # TODO send pdf to storage eg. S3
    # TODO update job status in pg, inc. storage url
    await asyncio.sleep(5)
    print('finished', raw_data)


def run_worker():
    loop = asyncio.get_event_loop()

    # TODO deal with SIGTERM gracefully
    async def go():
        redis = await aioredis.create_redis(('localhost', 6379), loop=loop)
        while True:
            queue, data = await redis.blpop(*QUEUES)
            task = asyncio.ensure_future(work(data))
            await task
        redis.close()

    loop.run_until_complete(go())


if __name__ == '__main__':
    run_worker()
