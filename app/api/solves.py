from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.solve import Solve, PenaltyType
from app.schemas.solve import SolveCreate, SolveUpdate, SolveResponse, StatsResponse
from app.services.scrambler import generate_scramble_3x3
from app.services.stats import compute_wca_stats, format_time

router = APIRouter(prefix="/api/solves", tags=["solves"])


def _to_solve_response(solve: Solve) -> SolveResponse:
    return SolveResponse(
        id=solve.id,
        user_id=solve.user_id,
        raw_time_ms=solve.raw_time_ms,
        final_time_ms=solve.final_time_ms,
        formatted_time=format_time(solve.final_time_ms, penalty=solve.penalty),
        penalty=solve.penalty,
        scramble=solve.scramble,
        created_at=solve.created_at
    )


@router.get("/scramble")
async def get_new_scramble():
    """Returns a fresh, valid WCA 3x3x3 scramble."""
    scramble = generate_scramble_3x3()
    return {"scramble": scramble}


@router.post("", response_model=SolveResponse, status_code=status.HTTP_201_CREATED)
async def create_solve(
    solve_in: SolveCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Save a completed solve for the authenticated user."""
    solve = Solve(
        user_id=current_user.id,
        raw_time_ms=solve_in.raw_time_ms,
        penalty=solve_in.penalty,
        scramble=solve_in.scramble
    )
    db.add(solve)
    await db.flush()
    await db.refresh(solve)
    return _to_solve_response(solve)


@router.get("", response_model=List[SolveResponse])
async def list_solves(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve history of user solves (newest first)."""
    stmt = (
        select(Solve)
        .where(Solve.user_id == current_user.id)
        .order_by(desc(Solve.created_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    solves = result.scalars().all()
    return [_to_solve_response(s) for s in solves]


@router.get("/stats", response_model=StatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Calculate and return WCA statistics (PB, ao5, ao12, ao100) for the user."""
    # Fetch all solves in chronological order
    stmt = (
        select(Solve)
        .where(Solve.user_id == current_user.id)
        .order_by(Solve.created_at.asc())
    )
    result = await db.execute(stmt)
    solves = result.scalars().all()

    stats_dict = compute_wca_stats(solves)
    return StatsResponse(**stats_dict)


@router.patch("/{solve_id}", response_model=SolveResponse)
async def update_solve_penalty(
    solve_id: int,
    solve_update: SolveUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update penalty (+2, DNF, none) for an existing solve."""
    stmt = select(Solve).where(Solve.id == solve_id, Solve.user_id == current_user.id)
    result = await db.execute(stmt)
    solve = result.scalar_one_or_none()

    if not solve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solve not found"
        )

    solve.penalty = solve_update.penalty
    await db.flush()
    await db.refresh(solve)
    return _to_solve_response(solve)


@router.delete("/{solve_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_solve(
    solve_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a single solve from history."""
    stmt = select(Solve).where(Solve.id == solve_id, Solve.user_id == current_user.id)
    result = await db.execute(stmt)
    solve = result.scalar_one_or_none()

    if not solve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solve not found"
        )

    await db.delete(solve)
    await db.flush()
    return None
