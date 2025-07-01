from fastapi import APIRouter

router = APIRouter()


@router.post("/test/war")
async def test_war():
    return {
        "Hello World"
    }