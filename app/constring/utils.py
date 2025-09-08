import aioodbc


async def test_connection_async(con_str: str) -> bool:
    try:
        async with aioodbc.connect(dsn=con_str, timeout=5) as conn:
            return True
    except Exception as e:
        print(f"Test connection failed: {e}")
        return False
