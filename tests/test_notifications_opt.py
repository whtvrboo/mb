from sqlalchemy import inspect

from mitlist.modules.notifications.models import Comment, Notification, Reaction


def test_notification_indexes():
    """Verify indexes on Notification model."""
    mapper = inspect(Notification)
    # SQLAlchemy Core stores indexes in the table object associated with the mapper
    table = mapper.local_table

    indexes = {idx.name: idx for idx in table.indexes}

    assert "ix_notifications_user_lookup" in indexes
    idx = indexes["ix_notifications_user_lookup"]

    # Check columns
    column_names = [c.name for c in idx.columns]
    assert column_names == ["user_id", "created_at"]

    # Verify user_id is NOT indexed individually
    # (unless implicitly via FK, but we removed explicit index=True)
    # Note: indexes list only contains explicitly defined indexes.
    # user_id might still have an index if the backend creates one for FK automatically,
    # but at model level, we shouldn't see "ix_notifications_user_id" if we removed index=True.
    # Standard naming for index=True on column 'user_id' is 'ix_notifications_user_id' usually.

    assert "ix_notifications_user_id" not in indexes


def test_comment_indexes():
    """Verify indexes on Comment model."""
    mapper = inspect(Comment)
    table = mapper.local_table

    indexes = {idx.name: idx for idx in table.indexes}

    assert "ix_comments_parent_lookup" in indexes
    idx = indexes["ix_comments_parent_lookup"]

    column_names = [c.name for c in idx.columns]
    assert column_names == ["parent_type", "parent_id", "created_at"]

    # Verify parent_id is NOT indexed individually
    assert "ix_comments_parent_id" not in indexes


def test_reaction_indexes():
    """Verify indexes on Reaction model."""
    mapper = inspect(Reaction)
    table = mapper.local_table

    indexes = {idx.name: idx for idx in table.indexes}

    assert "ix_reactions_target_lookup" in indexes
    idx = indexes["ix_reactions_target_lookup"]

    column_names = [c.name for c in idx.columns]
    assert column_names == ["target_type", "target_id"]

    # Verify target_id is NOT indexed individually
    assert "ix_reactions_target_id" not in indexes
