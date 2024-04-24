import os
import time
import httpx
import argparse
import asyncio
import aiofiles
from onlylog import Log
from colorama import init, Fore

init(autoreset=True)
magenta = Fore.LIGHTMAGENTA_EX
hijau = Fore.LIGHTGREEN_EX
biru = Fore.LIGHTBLUE_EX


async def http_checker(
    host: str = "http://httpbin.org/ip",
    proxy: str = None,
    timeout: int = 300,
):
    try:
        if "https://" in proxy:
            proxy = proxy.replace("https://", "")

        if "http://" not in proxy:
            proxy = "http://" + proxy

        async with httpx.AsyncClient(proxy=proxy, verify=False) as client:
            start = int(time.time())
            res = await client.get(host, timeout=timeout)
            end = int(time.time())
            total = end - start
            if res.status_code == 200:
                Log.success(f"{proxy} GOOD PROXY ({total} ms)!")
                async with aiofiles.open("http.txt", "a+") as w:
                    await w.write(f"{proxy}\n")
                return

            Log.error(f"{proxy} BAD PROXY !")
    except (
        httpx.ProxyError,
        httpx.ConnectError,
        httpx.RemoteProtocolError,
        httpx.ReadError,
    ):
        Log.error(f"{proxy} BAD PROXY ")


async def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(
        f"""{magenta}
___  ____ ____ _  _ _   _    ____ _  _ ____ ____ _  _ ____ ____ 
|__] |__/ |  |  \/   \_/     |    |__| |___ |    |_/  |___ |__/ 
|    |  \ |__| _/\_   |      |___ |  | |___ |___ | \_ |___ |  \ 
                                                                
\t{hijau}Author: AkasakaID
          """
    )
    args = argparse.ArgumentParser(
        description="""
Just Proxy Checker
    """
    )
    args.add_argument("--file", "-F", required=True, help="List proxy files")
    args.add_argument(
        "--host",
        "-H",
        required=False,
        help="Target host for proxy checking. Default: http://httpbin.org/ip",
        default="http://httpbin.org/ip",
    )
    args.add_argument(
        "--timeout",
        "-T",
        required=False,
        help="Timeout for http request. Default: 300 seconds",
        default=300,
    )
    param = args.parse_args()
    async with aiofiles.open(param.file, "r") as op:
        _buff_proxy = await op.read()
        list_proxy = _buff_proxy.splitlines()
        tasks = [
            asyncio.ensure_future(
                http_checker(proxy=p, host=param.host, timeout=param.timeout)
            )
            for p in list_proxy
        ]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit()
