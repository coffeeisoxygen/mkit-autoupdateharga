"""schemas."""

from enum import StrEnum

from pydantic import BaseModel, ValidationError, field_validator


class ProductInDB(BaseModel):
    kode: str
    deskripsi: str
    harga: int
    status: str
    # created_at: datetime just trust in database
    # updated_at: datetime just trust in database


class WebResponseType(StrEnum):
    JSON = "json"
    HTML = "html"


class Supplier(BaseModel):
    name: str
    url_harga: str
    id_oto_modul: int
    web_response_type: WebResponseType
    mapping: dict[str, str] | None = None
    status_mapping: dict[str, str] | None = None
    is_active: bool = True

    model_config = {
        "extra": "forbid",
        "from_attributes": True,
        "populate_by_name": True,
    }

    @field_validator("mapping")
    def validate_mapping(cls, v):
        # Ambil field dari ProductInDB secara dinamis
        allowed_keys = set(ProductInDB.model_fields.keys())
        if v is not None:
            for k in v.keys():
                if k not in allowed_keys:
                    raise ValidationError(f"Invalid mapping key: {k}")
        return v

    def normalize_status(self, raw_status: str) -> str:
        """
        Normalisasi status produk supplier ke '1' (aktif) atau '0' (nonaktif) sesuai status_mapping.
        Jika tidak ditemukan di mapping, default ke '0'.
        """
        if self.status_mapping:
            return self.status_mapping.get(str(raw_status).lower(), "0")
        return "0"
