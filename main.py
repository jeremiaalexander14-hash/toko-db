
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel, select
import bcrypt

from auth import verifikasi_api_key
from database import engine
from models import (
    Produk,
    User,
    LoginRequest,
    UserPublic,
    ResponseProduk,
    ResponseProdukList,
    ResponseUser,
    ResponseUserList
)

app = FastAPI(title="API Toko")

# KONFIGURASI CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# HANDLER VALIDASI
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Data tidak valid",
            "detail": exc.errors()
        }
    )


# HANDLER HTTP EXCEPTION
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail
        }
    )


# HALAMAN UTAMA
@app.get("/")
def home():
    return {"message": "Selamat datang di API Toko"}


@app.post("/login", response_model=ResponseUser)
def login(kredensial: LoginRequest):
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.username == kredensial.username)
        ).first()

        if not user or not bcrypt.checkpw(
            kredensial.password.encode("utf-8"),
            user.password.encode("utf-8")
        ):
            raise HTTPException(status_code=401, detail="Username atau password salah")

        return {
            "success": True,
            "message": "Login berhasil",
            "data": UserPublic(
                id=user.id,
                nama=user.nama,
                username=user.username,
                role=user.role
            )
        }


# =========================
# CRUD PRODUK
# =========================

@app.get(
    "/produk",
    response_model=ResponseProdukList,
    dependencies=[Depends(verifikasi_api_key)]
)
def get_produk():
    with Session(engine) as session:
        data = session.exec(select(Produk)).all()
        return {
            "success": True,
            "message": "Data produk berhasil ditampilkan",
            "data": data
        }


@app.get(
    "/produk/{id}",
    response_model=ResponseProduk,
    dependencies=[Depends(verifikasi_api_key)]
)
def get_produk_by_id(id: int):
    with Session(engine) as session:
        data = session.get(Produk, id)

        if not data:
            raise HTTPException(status_code=404, detail="Produk tidak ditemukan")

        return {
            "success": True,
            "message": "Data produk berhasil ditemukan",
            "data": data
        }


@app.post(
    "/produk",
    response_model=ResponseProduk,
    status_code=201,
    dependencies=[Depends(verifikasi_api_key)]
)
def tambah_produk(produk_baru: Produk):
    with Session(engine) as session:
        produk_baru.id = None
        session.add(produk_baru)
        session.commit()
        session.refresh(produk_baru)

        return {
            "success": True,
            "message": "Produk berhasil ditambahkan",
            "data": produk_baru
        }


@app.put(
    "/produk/{id}",
    response_model=ResponseProduk,
    dependencies=[Depends(verifikasi_api_key)]
)
def update_produk(id: int, produk_baru: Produk):
    with Session(engine) as session:
        data = session.get(Produk, id)

        if not data:
            raise HTTPException(status_code=404, detail="Produk tidak ditemukan")

        data.nama = produk_baru.nama
        data.harga = produk_baru.harga
        data.stok = produk_baru.stok
        data.kategori = produk_baru.kategori

        session.add(data)
        session.commit()
        session.refresh(data)

        return {
            "success": True,
            "message": "Produk berhasil diubah",
            "data": data
        }


@app.delete(
    "/produk/{id}",
    response_model=ResponseProduk,
    dependencies=[Depends(verifikasi_api_key)]
)
def delete_produk(id: int):
    with Session(engine) as session:
        data = session.get(Produk, id)

        if not data:
            raise HTTPException(status_code=404, detail="Produk tidak ditemukan")

        data_produk = data.model_dump()
        session.delete(data)
        session.commit()

        return {
            "success": True,
            "message": "Produk berhasil dihapus",
            "data": data_produk
        }


# =========================
# CRUD USER
# =========================

@app.get(
    "/user",
    response_model=ResponseUserList,
    dependencies=[Depends(verifikasi_api_key)]
)
def get_user():
    with Session(engine) as session:
        data = session.exec(select(User)).all()

        return {
            "success": True,
            "message": "Data user berhasil ditampilkan",
            "data": data
        }


@app.get(
    "/user/{id}",
    response_model=ResponseUser,
    dependencies=[Depends(verifikasi_api_key)]
)
def get_user_by_id(id: int):
    with Session(engine) as session:
        data = session.get(User, id)

        if not data:
            raise HTTPException(status_code=404, detail="User tidak ditemukan")

        return {
            "success": True,
            "message": "Data user berhasil ditemukan",
            "data": data
        }


@app.post(
    "/user",
    response_model=ResponseUser,
    status_code=201,
    dependencies=[Depends(verifikasi_api_key)]
)
def tambah_user(user_baru: User):
    with Session(engine) as session:
        user_baru.id = None

        password_hash = bcrypt.hashpw(
            user_baru.password.encode("utf-8"),
            bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

        user_baru.password = password_hash

        session.add(user_baru)
        session.commit()
        session.refresh(user_baru)

        return {
            "success": True,
            "message": "User berhasil ditambahkan",
            "data": user_baru
        }


@app.put(
    "/user/{id}",
    response_model=ResponseUser,
    dependencies=[Depends(verifikasi_api_key)]
)
def update_user(id: int, user_baru: User):
    with Session(engine) as session:
        data = session.get(User, id)

        if not data:
            raise HTTPException(status_code=404, detail="User tidak ditemukan")

        data.nama = user_baru.nama
        data.username = user_baru.username
        data.role = user_baru.role

        password_hash = bcrypt.hashpw(
            user_baru.password.encode("utf-8"),
            bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

        data.password = password_hash

        session.add(data)
        session.commit()
        session.refresh(data)

        return {
            "success": True,
            "message": "User berhasil diubah",
            "data": data
        }


@app.delete(
    "/user/{id}",
    response_model=ResponseUser,
    dependencies=[Depends(verifikasi_api_key)]
)
def delete_user(id: int):
    with Session(engine) as session:
        data = session.get(User, id)

        if not data:
            raise HTTPException(status_code=404, detail="User tidak ditemukan")

        data_user = UserPublic(
            id=data.id,
            nama=data.nama,
            username=data.username,
            role=data.role
        )

        session.delete(data)
        session.commit()

        return {
            "success": True,
            "message": "User berhasil dihapus",
            "data": data_user
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
