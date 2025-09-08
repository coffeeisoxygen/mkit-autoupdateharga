from abc import ABC, abstractmethod

import httpx
from bs4 import BeautifulSoup
from loguru import logger
from schemas import ProductInDB, Supplier, WebResponseType


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
            try:
                status = supplier.normalize_status(
                    item.get(supplier.mapping["status"], "")
                )
                products.append(
                    ProductInDB(
                        kode=item.get(supplier.mapping["kode"], ""),
                        deskripsi=item.get(supplier.mapping["deskripsi"], ""),
                        harga=int(float(item.get(supplier.mapping["harga"], 0))),
                        status=status,
                    )
                )
            except Exception as e:
                logger.warning(f"[{supplier.name}] gagal parse item JSON: {e}")
                continue

        return products


class HtmlFetchStrategy(FetchStrategy):
    async def fetch(self, supplier: Supplier) -> list[ProductInDB]:
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
                try:
                    kode = cols[0].get_text(strip=True)
                    deskripsi = cols[1].get_text(strip=True)
                    harga = (
                        cols[2].get_text(strip=True).replace(".", "").replace(",", "")
                    )
                    status_raw = cols[3].get_text(strip=True)

                    harga_int = (
                        int(float(harga))
                        if harga.isdigit() or harga.replace(".", "").isdigit()
                        else 0
                    )
                    status = supplier.normalize_status(status_raw)

                    products.append(
                        ProductInDB(
                            kode=kode,
                            deskripsi=deskripsi,
                            harga=harga_int,
                            status=status,
                        )
                    )
                except Exception as e:
                    logger.warning(f"[{supplier.name}] gagal parse row HTML: {e}")
                    continue

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
