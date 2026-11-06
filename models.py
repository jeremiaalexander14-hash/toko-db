
from sqlmodel import SQLModel, Field
from typing import Optional


# TABEL PRODUK
class Produk(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nama: str
    harga: float
    stok: int
    kategori: str


# TABEL USER
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nama: str
    username: str
    password: str
    role: str = Field(default="user")


class LoginRequest(SQLModel):
    username: str
    password: str


# RESPONSE PRODUK
class ResponseProduk(SQLModel):
    success: bool
    message: str
    data: Optional[Produk] = None


class ResponseProdukList(SQLModel):
    success: bool
    message: str
    data: list[Produk]


# RESPONSE USER PUBLIK (TANPA PASSWORD)
class UserPublic(SQLModel):
    id: int
    nama: str
    username: str
    role: str


# RESPONSE USER
class ResponseUser(SQLModel):
    success: bool
    message: str
    data: Optional[UserPublic] = None


class ResponseUserList(SQLModel):
    success: bool
    message: str
    data: list[UserPublic]
