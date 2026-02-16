import asyncio
from aiomql import ResultDB, Result, TradeRecords

async def update_sql_records():
    tr = TradeRecords()
    # await tr.update_sql_records()
    # await tr.update_csv_records()
    await tr.update_json_records()


def to_csv():
    ResultDB.dump_to_csv()


if __name__ == "__main__":
    asyncio.run(update_sql_records())
    # to_csv()
