from abc import ABC, abstractmethod

import httpx
from bs4 import BeautifulSoup
from loguru import logger
from schemas import ProductInDB, Supplier, WebResponseType


def parse_product_item(item: dict, supplier: Supplier) -> ProductInDB | None:
    if supplier.mapping is None:
        return None
    try:
        status = supplier.normalize_status(
            item.get(supplier.mapping.get("status", ""), "")
        )
        return ProductInDB(
            kode=item.get(supplier.mapping.get("kode", ""), ""),
            deskripsi=item.get(supplier.mapping.get("deskripsi", ""), ""),
            harga=int(float(item.get(supplier.mapping.get("harga", ""), 0))),
            status=status,
        )
    except Exception as e:
        logger.warning(f"[{supplier.name}] gagal parse item: {e}")
        return None


class FetchStrategy(ABC):
    @abstractmethod
    async def fetch(self, supplier: Supplier) -> list[ProductInDB]:
        pass


class JsonFetchStrategy(FetchStrategy):
    async def fetch(self, supplier: Supplier) -> list[ProductInDB]:
        if supplier.mapping is None:
            logger.warning(f"[{supplier.name}] mapping kosong, skip.")
            return []

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(str(supplier.url_harga))
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                logger.error(f"[{supplier.name}] gagal fetch JSON: {e}")
                return []

        # Kalau bentuk dict tapi key `data`, ambil isi nya
        items = data.get("data", data) if isinstance(data, dict) else data
        products: list[ProductInDB] = []

        for item in items:
            product = parse_product_item(item, supplier)
            if product:
                products.append(product)
        return products


class HtmlFetchStrategy(FetchStrategy):
    async def fetch(self, supplier: Supplier) -> list[ProductInDB]:
        if supplier.mapping is None:
            logger.warning(f"[{supplier.name}] mapping kosong, skip.")
            return []
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(str(supplier.url_harga))
                resp.raise_for_status()
            except Exception as e:
                logger.error(f"[{supplier.name}] gagal fetch HTML: {e}")
                return []

        soup = BeautifulSoup(resp.text, "html.parser")
        products: list[ProductInDB] = []

        for row in soup.select("table.tabel tr"):
            cols = row.find_all("td")
            if len(cols) == 4 and cols[0].get_text(strip=True).lower() != "kode":
                item = {
                    supplier.mapping.get("kode", "kode"): cols[0].get_text(strip=True),
                    supplier.mapping.get("deskripsi", "deskripsi"): cols[1].get_text(
                        strip=True
                    ),
                    supplier.mapping.get("harga", "harga"): cols[2]
                    .get_text(strip=True)
                    .replace(".", "")
                    .replace(",", ""),
                    supplier.mapping.get("status", "status"): cols[3].get_text(
                        strip=True
                    ),
                }
                # harga conversion
                try:
                    harga_val = item[supplier.mapping.get("harga", "harga")]
                    harga_int = (
                        int(float(harga_val))
                        if harga_val.isdigit() or harga_val.replace(".", "").isdigit()
                        else 0
                    )
                    item[supplier.mapping.get("harga", "harga")] = str(harga_int)
                except Exception:
                    item[supplier.mapping.get("harga", "harga")] = "0"
                product = parse_product_item(item, supplier)
                if product:
                    products.append(product)
        return products


class FetchContext:
    def __init__(self, supplier: Supplier):
        # Auto pilih strategy
        if supplier.web_response_type == WebResponseType.JSON:
            self._strategy: FetchStrategy = JsonFetchStrategy()
        elif supplier.web_response_type == WebResponseType.HTML:
            self._strategy: FetchStrategy = HtmlFetchStrategy()
        else:
            raise ValueError(
                f"Tipe response {supplier.web_response_type} belum didukung."
            )

    async def fetch(self, supplier: Supplier) -> list[ProductInDB]:
        return await self._strategy.fetch(supplier)
