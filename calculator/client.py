import asyncio
import random
import argparse
import json

import httpx
import pandas as pd


async def calculate(rand_range: int = 10):
    X = random.randrange(1, rand_range)
    uid = httpx.get(f'http://0.0.0.0:8082/calculate?X={X}').json()
    print("X = ", X, "uid = ", uid)
    result = await get_result(uid)
    print("_" * 50)
    print("X = ", X, "uid = ", uid)
    print("_" * 50)
    result = pd.DataFrame(json.loads(result))
    print(result)
    return result


async def get_result(uid: str):
    s = 0
    while s != 200:
        await asyncio.sleep(1)
        r = httpx.get(f'http://0.0.0.0:8082/result?uid={uid}')
        s = r.status_code
    return r.json()


async def test_async_client(req_num: int, rand_range: int):
    for f in asyncio.as_completed([calculate(rand_range) for _ in range(req_num)]):
        await f


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Client.')
    parser.add_argument('--req_num', help='number of requests')
    parser.add_argument('--rand_range', help='rand X from 1 to rand_range')
    args = parser.parse_args()

    req_num = args.req_num or 5
    rand_range = args.rand_range or 10

    asyncio.run(test_async_client(req_num, rand_range))
