from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Type

from solvers.base_solver import BaseSolver
from solvers.nearest_neighbor import NearestNeighborSolver


@dataclass(frozen=True)
class SolverSpec:
    slug: str
    display_name: str
    description: str
    module: str
    class_name: str
    requires: Optional[str] = None


def _load_solver_class(module: str, class_name: str) -> Optional[Type[BaseSolver]]:
    try:
        module_obj = __import__(module, fromlist=[class_name])
        cls: Type[BaseSolver] = getattr(module_obj, class_name)
        return cls
    except (ImportError, AttributeError):
        return None


def _registered_specs() -> List[SolverSpec]:
    specs: List[SolverSpec] = [
        SolverSpec(
            slug="nearest_neighbor",
            display_name="Nearest Neighbor",
            description="Greedy heuristic that builds the route by always visiting the nearest unvisited stop.",
            module="solvers.nearest_neighbor",
            class_name="NearestNeighborSolver",
        ),
        SolverSpec(
            slug="held_karp",
            display_name="Held-Karp (Dynamic Programming)",
            description="Optimal solver using dynamic programming; scales exponentially with the number of stops.",
            module="solvers.held_karp",
            class_name="HeldKarpSolver",
        ),
        SolverSpec(
            slug="branch_and_bound",
            display_name="Branch & Bound",
            description="Optimal solver with pruning; faster than brute force on many practical instances.",
            module="solvers.branch_and_bound",
            class_name="BranchAndBoundSolver",
        ),
        SolverSpec(
            slug="rl_solver",
            display_name="Reinforcement Learning Solver",
            description="Neural network guided heuristic (requires PyTorch and trained weights).",
            module="solvers.rl_solver",
            class_name="RLSolver",
            requires="torch",
        ),
    ]
    return specs


def get_solver_specs(include_unavailable: bool = False) -> List[Dict[str, str]]:
    """
    Return metadata for known solvers.
    """
    available_specs: List[Dict[str, str]] = []

    for spec in _registered_specs():
        cls = _load_solver_class(spec.module, spec.class_name)
        if cls is None and not include_unavailable:
            continue

        available_specs.append(
            {
                "slug": spec.slug,
                "name": spec.display_name,
                "description": spec.description,
                "requires": spec.requires or "",
                "available": cls is not None,
            }
        )

    return available_specs


def get_solver_class(slug: str) -> Optional[Type[BaseSolver]]:
    if slug == "nearest_neighbor":
        return NearestNeighborSolver

    for spec in _registered_specs():
        if spec.slug == slug:
            return _load_solver_class(spec.module, spec.class_name)
    return None


def instantiate_solvers(slugs: Iterable[str]) -> List[BaseSolver]:
    instances: List[BaseSolver] = []
    seen = set()

    for slug in slugs:
        if slug in seen:
            continue
        seen.add(slug)

        cls = get_solver_class(slug)
        if cls is None:
            raise ValueError(f"Solver '{slug}' is not available.")

        solver = cls()
        if not isinstance(solver, BaseSolver):
            raise TypeError(f"Solver '{slug}' does not inherit from BaseSolver.")
        instances.append(solver)

    if not instances:
        raise ValueError("No valid solvers selected.")

    return instances


def default_solver_slugs() -> List[str]:
    """
    Convenience helper for UIs that want all currently available solvers.
    """
    return [spec["slug"] for spec in get_solver_specs()]



