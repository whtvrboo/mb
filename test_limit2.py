import pytest
from pydantic import ValidationError
from mitlist.modules.notifications.schemas import CommentCreate

def test_comment_limits():
    try:
        CommentCreate(
            parent_id=1,
            parent_type="EXPENSE",
            content="Test",
            mentioned_user_ids=[1] * 101
        )
        assert False, "Should raise ValidationError"
    except ValidationError as e:
        print("com error:", e)

if __name__ == "__main__":
    test_comment_limits()
