from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse

from frigate.api.auth import require_role
from frigate.api.defs.tags import Tags
from frigate.config import FrigateConfig
from frigate.util.builtin import update_yaml_from_url
from frigate.util.config import find_config_file

router = APIRouter(tags=[Tags.zones])


@router.get("/zones/{camera}/{zone}/direction")
def get_zone_direction(request: Request, camera: str, zone: str):
    config: FrigateConfig = request.app.frigate_config
    camera_cfg = config.cameras.get(camera)
    if not camera_cfg or zone not in camera_cfg.zones:
        return JSONResponse(status_code=404, content="Zone not found")

    return {"angle_range": camera_cfg.zones[zone].angle_range}


@router.put(
    "/zones/{camera}/{zone}/direction",
    dependencies=[Depends(require_role(["admin"]))],
)
def set_zone_direction(
    request: Request,
    camera: str,
    zone: str,
    body: dict = Body(...),
):
    angle_range = body.get("angle_range")
    if (
        angle_range is None
        or not isinstance(angle_range, list)
        or len(angle_range) != 2
    ):
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "angle_range list required"},
        )

    angle_str = f"{angle_range[0]},{angle_range[1]}"

    config_file = find_config_file()
    try:
        update_yaml_from_url(
            config_file,
            f"?cameras.{camera}.zones.{zone}.angle_range={angle_str}",
        )
        with open(config_file, "r") as f:
            new_raw_config = f.read()

        config = FrigateConfig.parse_yaml(new_raw_config)
        request.app.frigate_config = config
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": str(e)}, status_code=400
        )

    return JSONResponse(content={"success": True, "angle_range": angle_range})
