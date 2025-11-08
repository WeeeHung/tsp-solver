from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote_plus

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from runner.solver_runner import SolverRunner
from utils.solver_factory import (
    default_solver_slugs,
    get_solver_specs,
    instantiate_solvers,
)

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
INDEX_HTML = FRONTEND_DIR / "index.html"

app = FastAPI(title="TSP Solver Web UI", version="1.0.0")

if FRONTEND_DIR.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_DIR), html=False),
        name="frontend-assets",
    )


class SolveRequest(BaseModel):
    locations: List[str] = Field(..., min_length=2)
    solvers: Optional[List[str]] = None
    region: str = Field(default="sg", min_length=2, max_length=10)

    @field_validator("locations", mode="before")
    @classmethod
    def normalize_locations(cls, value):
        if isinstance(value, str):
            items = [line.strip() for line in value.splitlines() if line.strip()]
        elif isinstance(value, list):
            items = [str(item).strip() for item in value if str(item).strip()]
        else:
            raise TypeError("locations must be provided as a newline string or list.")

        if len(items) < 2:
            raise ValueError("At least two locations are required.")

        return items

    @field_validator("solvers", mode="before")
    @classmethod
    def normalize_solvers(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            return [slug.strip() for slug in value.split(",") if slug.strip()]
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        raise TypeError("solvers must be a list or comma-separated string.")


class RouteLocation(BaseModel):
    id: Optional[str] = ""
    name: str = ""
    formatted_address: str = ""
    lat: Optional[float] = None
    lon: Optional[float] = None


class SolveResponse(BaseModel):
    solver: str
    total_distance_km: float
    solve_time_s: float
    num_locations: int
    route: List[RouteLocation]
    map_embed_url: Optional[str]
    map_share_url: Optional[str]


@app.get("/api/solvers")
def list_solvers():
    return {"solvers": get_solver_specs(include_unavailable=True)}


@app.post("/api/solve")
def solve_tsp(request: SolveRequest):
    selected_slugs = request.solvers or default_solver_slugs()

    try:
        solvers = instantiate_solvers(selected_slugs)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    runner = SolverRunner(use_google_maps=True)

    try:
        runner.load_locations_from_names(
            location_names=request.locations,
            region=request.region,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not runner.locations:
        raise HTTPException(
            status_code=400,
            detail="No locations were successfully geocoded.",
        )

    instance = {
        "name": f"Custom Tour ({len(runner.locations)} stops)",
        "locations": [loc["id"] for loc in runner.locations],
    }

    responses: List[SolveResponse] = []

    for solver in solvers:
        result = runner.run_solver_on_instance(solver, instance)
        route_locations = result.get("route_locations", [])

        embed_url, share_url = _build_google_maps_urls(route_locations)

        responses.append(
            SolveResponse(
                solver=result.get("solver_name", solver.name),
                total_distance_km=round(float(result.get("total_distance", 0.0)), 3),
                solve_time_s=round(float(result.get("solve_time", 0.0)), 4),
                num_locations=int(result.get("num_locations", len(route_locations))),
                route=[RouteLocation(**data) for data in _serialize_route(route_locations)],
                map_embed_url=embed_url,
                map_share_url=share_url,
            )
        )

    return {"results": [response.model_dump() for response in responses]}


@app.get("/")
def serve_frontend():
    if not INDEX_HTML.exists():
        raise HTTPException(
            status_code=404,
            detail="Frontend assets not found. Build or create the webapp/frontend files.",
        )
    return FileResponse(str(INDEX_HTML))


def _serialize_route(route_locations: List[Dict]) -> List[Dict[str, Any]]:
    serialized = []
    for loc in route_locations:
        serialized.append(
            {
                "id": str(loc.get("id", "")),
                "name": loc.get("name", ""),
                "formatted_address": loc.get("formatted_address", ""),
                "lat": loc.get("lat"),
                "lon": loc.get("lon"),
            }
        )
    return serialized


def _build_google_maps_urls(
    route_locations: List[Dict],
) -> Tuple[Optional[str], Optional[str]]:
    if not GOOGLE_MAPS_API_KEY:
        return None, None
    if len(route_locations) < 2:
        return None, None

    coords = []
    for loc in route_locations:
        lat = loc.get("lat")
        lon = loc.get("lon")
        if lat is None or lon is None:
            return None, None
        coords.append((lat, lon))

    origin = coords[0]
    destination = coords[-1]
    waypoints = coords[1:-1]

    embed_url = _compose_embed_url(origin, destination, waypoints)
    share_url = _compose_share_url(origin, destination, waypoints)
    return embed_url, share_url


def _compose_embed_url(
    origin: Tuple[float, float],
    destination: Tuple[float, float],
    waypoints: List[Tuple[float, float]],
) -> str:
    base = (
        "https://www.google.com/maps/embed/v1/directions"
        f"?key={quote_plus(GOOGLE_MAPS_API_KEY)}"
        f"&origin={_encode_coord(origin)}"
        f"&destination={_encode_coord(destination)}"
        "&mode=driving"
    )
    trimmed = _trim_waypoints(waypoints)
    if trimmed:
        base += f"&waypoints={'|'.join(_encode_coord(wp) for wp in trimmed)}"
    return base


def _compose_share_url(
    origin: Tuple[float, float],
    destination: Tuple[float, float],
    waypoints: List[Tuple[float, float]],
) -> str:
    base = (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={_encode_coord(origin)}"
        f"&destination={_encode_coord(destination)}"
        "&travelmode=driving"
    )
    trimmed = _trim_waypoints(waypoints, max_points=25)  # Share URLs allow more waypoints
    if trimmed:
        base += f"&waypoints={'|'.join(_encode_coord(wp) for wp in trimmed)}"
    return base


def _trim_waypoints(
    waypoints: List[Tuple[float, float]],
    max_points: int = 23,
) -> List[Tuple[float, float]]:
    if len(waypoints) <= max_points:
        return waypoints
    # Evenly sample waypoints to respect API limits while preserving overall shape
    step = max(1, len(waypoints) // max_points)
    trimmed = waypoints[::step][:max_points]
    return trimmed


def _encode_coord(coord: Tuple[float, float]) -> str:
    lat, lon = coord
    return quote_plus(f"{lat},{lon}")

