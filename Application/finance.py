import datetime
import re
from typing import Dict

import aiohttp
from bs4 import BeautifulSoup


class NAVER:
    FINANCE_URL = "https://finance.naver.com/item/sise.nhn?code="
    REGEX_1 = re.compile("[^.0-9+-]")
    REGEX_2 = re.compile("[^:.,0-9]")
    REGEX_PAGE = re.compile("page=[0-9]*")

    @classmethod
    def get_stock_time_today(cls):
        return datetime.datetime.now().strftime("%Y%m%d") + "180000"

    @classmethod
    async def get_soup_object(cls, url):
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url) as res:
                return BeautifulSoup(await res.text(), "html.parser")

    @classmethod
    async def get_response(cls, url):
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url) as res:
                return await res.text()

    @classmethod
    async def get_last_page(cls, url):
        soup = await cls.get_soup_object(url)
        data = soup.select("td.pgRR > a")[0]['href']
        return int(cls.REGEX_PAGE.findall(data)[-1][5:])

    @classmethod
    async def get_stock_status(cls, code: str) -> Dict:
        soup = await cls.get_soup_object(cls.FINANCE_URL + code)

        title = soup.select("table.type2.type_tax > tbody > tr > th.title")
        data = soup.select("table.type2.type_tax > tbody > tr > td.num")

        result = {h.get_text(): float(cls.REGEX_1.sub("", d.get_text())) for (h, d) in zip(title, data)}

        return result

    @classmethod
    async def get_price_per_time(cls, code: str, page: int = None):
        today = cls.get_stock_time_today()

        if not page:
            page = await cls.get_last_page(f"https://finance.naver.com/item/sise_time.nhn?code={code}&thistime={today}")

        data = ""
        for x in range(1, page + 1):
            data += await cls.get_response(
                f"https://finance.naver.com/item/sise_time.nhn?code={code}&thistime={today}&page={x}")
        soup = BeautifulSoup(data, "html.parser")

        return {"cols": [x.get_text() for x in soup.select("table.type2 > tr")[0].select("th")],
                "data": [[cls.REGEX_2.sub("", v.get_text()) for v in tr.select("td > .tah")] for tr in
                         soup.select("table.type2 > tr[onmouseover]")]}

    @classmethod
    async def get_price_per_day(cls, code: str, page: int):
        data = ""
        for x in range(1, page + 1):
            data += await cls.get_response(
                f"https://finance.naver.com/item/sise_day.nhn?code={code}&page={x}")
        soup = BeautifulSoup(data, "html.parser")

        return {"cols": [x.get_text() for x in soup.select("table.type2 > tr")[0].select("th")],
                "data": [[cls.REGEX_2.sub("", v.get_text()) for v in tr.select("td > .tah")] for tr in
                         soup.select("table.type2 > tr[onmouseover]")]}


if __name__ == '__main__':
    import asyncio
    from pprint import pprint


    async def main():
        res = await NAVER.get_stock_status("005930")
        pprint(res, width=200)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
