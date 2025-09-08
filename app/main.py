"""experiment scrapping using request and beautifulsoup4.

the goal is to get the data from the url and save to file (later its will be saved to db).
"""

import asyncio
import json
from pathlib import Path

from fetch_strategy import FetchContext, WebResponseType
from loguru import logger
from schemas import Supplier


# --- Supplier Samples --------------------------------------------------------
def sample_supplier_json() -> Supplier:
    return Supplier(
        name="Supplier JSON Demo",
        url_harga="https://okeconnect.com/harga/json?id=905ccd028329b0a&produk=token_pln,ecommerce,digital,tagihan,air_pdam,finance,pascabayar,tagihan_pbb",
        id_oto_modul=1,
        web_response_type=WebResponseType.JSON,
        mapping={
            "kode": "kode",
            "deskripsi": "keterangan",
            "harga": "price",
            "status": "status",
        },
        status_mapping={
            "1": "1",
            "0": "0",
        },
        is_active=True,
    )


def sample_supplier_html() -> Supplier:
    return Supplier(
        name="Supplier HTML Demo",
        url_harga="https://bahara.webreport.info/harga.js.php?id=0f478e6166fab166b97d9113481992addc87d8ce7f29d2e4c0d90b0629deb7c880fd89d0d62e984e47b9bbf688023c8b-168",
        id_oto_modul=2,
        web_response_type=WebResponseType.HTML,
        mapping={
            "kode": "kode",
            "deskripsi": "keterangan",
            "harga": "harga",
            "status": "status",
        },
        status_mapping={
            "1": "Open",
            "0": "Gangguan",
        },
        is_active=True,
    )


# --- Core Logic --------------------------------------------------------------
async def fetch_and_save(supplier: Supplier, save_dir: Path) -> None:
    """Fetch data dari supplier dan simpan ke file JSON."""
    fetch_ctx = FetchContext(supplier)
    products = await fetch_ctx.fetch(supplier)

    logger.info(f"[{supplier.name}] total produk: {len(products)}")

    # Save ke file JSON
    save_path = save_dir / f"{supplier.name.replace(' ', '_').lower()}.json"
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump([p.dict() for p in products], f, ensure_ascii=False, indent=2)

    logger.success(f"[{supplier.name}] data berhasil disimpan ke {save_path}")


async def main():
    suppliers = [
        sample_supplier_json(),
        sample_supplier_html(),
    ]

    save_dir = Path("scraped_data")
    save_dir.mkdir(exist_ok=True)

    tasks = [fetch_and_save(s, save_dir) for s in suppliers]

    # Parallel fetch, kalau ada error tetap jalan untuk supplier lain
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Log error kalau ada exception
    for supplier, result in zip(suppliers, results):
        if isinstance(result, Exception):
            logger.error(f"[{supplier.name}] gagal fetch: {result}")


if __name__ == "__main__":
    asyncio.run(main())
