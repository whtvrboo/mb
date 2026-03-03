import pytest
from pydantic import ValidationError
from mitlist.modules.notifications.schemas import CommentCreate

def test_comment_limits():
    try:
        CommentCreate(
            parent_id=1,
            parent_type="POST",
            content="Test",
            mentioned_user_ids=[1] * 101
        )
        assert False, "Should raise ValidationError"
    except ValidationError as e:
        assert "at most 100 items" in str(e) or "too_long" in str(e)

if __name__ == "__main__":
    try: test_comment_limits()
    except Exception as e: print("com", e)
