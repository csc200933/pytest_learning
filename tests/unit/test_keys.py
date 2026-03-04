import pytest
import re
from tests.factories import pk_user, sk_profile

def test_dynamo_keys_rule_is_stable():
    assert pk_user("123") == "USER#123"
    assert sk_profile() == "PROFILE"

def test_pk_user_rejects_empty():
    with pytest.raises(ValueError, match=re.escape("user_id is required.")):
        pk_user("")