from fastapi import APIRouter

from motor import (
    MOTOR_NAME,
    STATUS,
    VERSION,
)


router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("")
def health():

    return {

        "status":
            "ok",

        "motor":
            MOTOR_NAME,

        "motor_version":
            VERSION,

        "motor_status":
            STATUS,
    }