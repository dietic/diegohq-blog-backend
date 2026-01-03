"""Contact form API endpoints."""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from src.dependencies import AsyncSessionDep, CurrentAdminUser
from src.models.contact_submission import ContactSubmission
from src.schemas.contact import (
    ContactReplyRequest,
    ContactSubmissionCreate,
    ContactSubmissionListResponse,
    ContactSubmissionResponse,
)

# Public router for contact form submission
public_router = APIRouter(prefix="/contact", tags=["Contact"])

# Admin router for managing contact submissions
admin_router = APIRouter(prefix="/admin/contact", tags=["Admin - Contact"])


# ============================================
# Public Endpoints
# ============================================


@public_router.post(
    "",
    response_model=ContactSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_contact_form(
    data: ContactSubmissionCreate,
    db: AsyncSessionDep,
) -> ContactSubmission:
    """Submit a contact form (public endpoint)."""
    submission = ContactSubmission(
        name=data.name,
        email=data.email,
        message=data.message,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission


# ============================================
# Admin Endpoints
# ============================================


@admin_router.get("", response_model=ContactSubmissionListResponse)
async def list_contact_submissions(
    _admin: CurrentAdminUser,
    db: AsyncSessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
) -> ContactSubmissionListResponse:
    """List all contact submissions (admin only)."""
    # Build query
    query = select(ContactSubmission).order_by(ContactSubmission.created_at.desc())

    if unread_only:
        query = query.where(ContactSubmission.is_read == False)  # noqa: E712

    # Get total count
    count_query = select(func.count()).select_from(ContactSubmission)
    if unread_only:
        count_query = count_query.where(ContactSubmission.is_read == False)  # noqa: E712
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get unread count
    unread_count_result = await db.execute(
        select(func.count())
        .select_from(ContactSubmission)
        .where(ContactSubmission.is_read == False)  # noqa: E712
    )
    unread_count = unread_count_result.scalar() or 0

    # Get items
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    items = list(result.scalars().all())

    return ContactSubmissionListResponse(
        items=items,
        total=total,
        unread_count=unread_count,
    )


@admin_router.get("/{submission_id}", response_model=ContactSubmissionResponse)
async def get_contact_submission(
    submission_id: UUID,
    _admin: CurrentAdminUser,
    db: AsyncSessionDep,
) -> ContactSubmission:
    """Get a specific contact submission (admin only)."""
    result = await db.execute(
        select(ContactSubmission).where(ContactSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact submission not found",
        )

    return submission


@admin_router.patch("/{submission_id}/read", response_model=ContactSubmissionResponse)
async def mark_as_read(
    submission_id: UUID,
    _admin: CurrentAdminUser,
    db: AsyncSessionDep,
) -> ContactSubmission:
    """Mark a contact submission as read (admin only)."""
    result = await db.execute(
        select(ContactSubmission).where(ContactSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact submission not found",
        )

    submission.is_read = True
    await db.commit()
    await db.refresh(submission)
    return submission


@admin_router.post("/{submission_id}/reply", response_model=ContactSubmissionResponse)
async def reply_to_submission(
    submission_id: UUID,
    data: ContactReplyRequest,
    admin: CurrentAdminUser,
    db: AsyncSessionDep,
) -> ContactSubmission:
    """Reply to a contact submission (admin only).

    This stores the reply and marks the submission as replied.
    Email sending should be handled separately (e.g., via a background task).
    """
    result = await db.execute(
        select(ContactSubmission).where(ContactSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact submission not found",
        )

    submission.reply_message = data.reply_message
    submission.is_replied = True
    submission.replied_at = datetime.now(UTC)
    submission.replied_by = admin.username
    submission.is_read = True  # Also mark as read

    await db.commit()
    await db.refresh(submission)
    return submission


@admin_router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact_submission(
    submission_id: UUID,
    _admin: CurrentAdminUser,
    db: AsyncSessionDep,
) -> None:
    """Delete a contact submission (admin only)."""
    result = await db.execute(
        select(ContactSubmission).where(ContactSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact submission not found",
        )

    await db.delete(submission)
    await db.commit()
