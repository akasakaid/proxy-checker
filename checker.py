import os
import time
import httpx
import argparse
import asyncio
import aiofiles
from colorama import init, Fore
import httpx_socks
from datetime import datetime

init(autoreset=True)
magenta = Fore.LIGHTMAGENTA_EX
green = Fore.LIGHTGREEN_EX
blue = Fore.LIGHTBLUE_EX
white = Fore.LIGHTWHITE_EX
red = Fore.LIGHTRED_EX


class ProxyModel:
    def __init__(self, scheme, user, pw, host, port):
        self.scheme = scheme
        self.user = user
        self.password = pw
        self.host = host
        self.port = port

    def to_dict(self):
        return {
            "scheme": self.scheme,
            "user": self.user,
            "password": self.password,
            "host": self.host,
            "port": self.port,
        }


class ProxyParser:
    @staticmethod
    def parser(proxy):
        s = proxy.split("://")
        scheme = s[0]
        ss = s[1].split("@")
        if len(ss) >= 2:
            user = ss[0].split(":")[0]
            pw = ss[0].split(":")[1]
            host = ss[1].split(":")[0]
            port = int(ss[1].split(":")[1])
            return ProxyModel(scheme, user, pw, host, port)
        host = ss[0].split(":")[0]
        port = int(ss[0].split(":")[1])
        return ProxyModel(scheme, None, None, host, port)


class ProxyChecker:
    def __init__(self, host, timeout, output):
        self.output = output
        self.host = host
        self.timeout = timeout

    async def checker(
        self,
        proxy: str = None,
    ):
        proxy_parser = ProxyParser.parser(proxy=proxy)
        try:
            transport = httpx_socks.AsyncProxyTransport.from_url(proxy)
            async with httpx.AsyncClient(transport=transport, verify=False) as client:
                start = time.time()
                res = await client.get(self.host, timeout=self.timeout)
                end = time.time()
                total = int(end - start)
                if res.status_code == 200:
                    print(
                        f"{white}-> {proxy_parser.host} {green}is good proxy, {white}{total}{green} ms !"
                    )
                    with open(self.output, "a+") as w:
                        w.write(f"{proxy}\n")
                    return
                print(f"{white}-> {proxy_parser.host} {red}is bad proxy")
        except:
            print(f"{white}-> {proxy_parser.host} {red}is bad proxy")


async def semapore(sem, host, timeout, proxy, output):
    async with sem:
        await ProxyChecker(host=host, timeout=timeout, output=output).checker(
            proxy=proxy
        )


async def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(
        f"""{magenta}                                                        
 _____                    _____ _           _           
|  _  |___ ___ _ _ _ _   |     | |_ ___ ___| |_ ___ ___ 
|   __|  _| . |_'_| | |  |   --|   | -_|  _| '_| -_|  _|
|__|  |_| |___|_,_|_  |  |_____|_|_|___|___|_,_|___|_|  
                  |___|                                 
{green}github.com/AkasakaID
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
        type=int,
    )
    args.add_argument(
        "--worker",
        "-W",
        help="Total worker for multi processing purpose. Default is cpu count / 2",
    )
    args = args.parse_args()
    async with aiofiles.open(args.file, "r") as op:
        _buff_proxy = await op.read()
        list_proxy = _buff_proxy.splitlines()
        if not args.worker:
            worker = int(os.cpu_count() / 2)
            if worker <= 0:
                worker = 1
        else:
            worker = int(args.worker)
        sema = asyncio.Semaphore(worker)
        output = datetime.now().isoformat().split("T")[0] + ".txt"
        tasks = [
            asyncio.create_task(
                semapore(
                    sem=sema,
                    proxy=p,
                    host=args.host,
                    timeout=args.timeout,
                    output=output,
                )
            )
            for p in list_proxy
        ]
        await asyncio.gather(*tasks)
        print(f"{green}result saved in : {white}{output}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit()
