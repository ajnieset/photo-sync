from fastapi import APIRouter

router = APIRouter(prefix="/upload")


@router.get("/")
async def get_uploads():
    return "uploading files"
