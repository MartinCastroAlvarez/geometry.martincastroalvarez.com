"""Tests for attributes package."""

import pytest
from attributes import Email
from attributes import Identifier
from attributes import Path
from attributes import ReceiptHandle
from attributes import Signature
from attributes import Url
from exceptions import PathMissingResourceIdError
from exceptions import ValidationError


class TestPath:
    """Test Path (API path string, normalized; version, resource, id)."""

    def test_path_empty(self):
        p = Path("")
        assert p == ""
        assert p.parts == []
        assert p.version == ""
        assert p.resource == ""

    def test_path_none_becomes_empty(self):
        p = Path(None)
        assert p == ""

    def test_path_strips_leading_slash(self):
        p = Path("/v1/galleries")
        assert p == "v1/galleries"

    def test_path_parts(self):
        p = Path("v1/galleries/abc-123")
        assert p.parts == ["v1", "galleries", "abc-123"]
        assert p.version == "v1"
        assert p.resource == "galleries"
        assert p.id == "abc-123"

    def test_path_id_raises_when_no_third_segment(self):
        p = Path("v1/galleries")
        with pytest.raises(PathMissingResourceIdError) as exc_info:
            _ = p.id
        assert "resource id" in str(exc_info.value).lower() or "id" in str(exc_info.value).lower()

    def test_path_startswith(self):
        p = Path("v1/galleries/xyz")
        assert p.startswith("v1/galleries")
        assert p.startswith("v1")
        assert not p.startswith("v2")


class TestIdentifier:
    """Test Identifier attribute."""

    def test_valid_string(self):
        assert Identifier("abc_123") == "abc_123"
        assert Identifier("x-y") == "x-y"

    def test_from_int(self):
        assert Identifier(42) == "42"

    def test_none_raises(self):
        with pytest.raises(ValidationError):
            Identifier(None)

    def test_empty_raises(self):
        with pytest.raises(ValidationError):
            Identifier("   ")

    def test_invalid_chars_raise(self):
        with pytest.raises(ValidationError):
            Identifier("bad space")
        with pytest.raises(ValidationError):
            Identifier("bad@mail")

    def test_non_string_non_int_raises(self):
        with pytest.raises(ValidationError):
            Identifier([])


class TestLimit:
    """Test Limit attribute."""

    def test_valid(self):
        from attributes import Limit

        assert Limit(20) == 20
        assert Limit(1) == 1
        assert Limit(1000) == 1000

    def test_none_defaults_to_20(self):
        from attributes import Limit

        assert Limit(None) == 20

    def test_below_min_raises(self):
        from attributes import Limit

        with pytest.raises(ValidationError):
            Limit(0)

    def test_above_max_raises(self):
        from attributes import Limit

        with pytest.raises(ValidationError):
            Limit(1001)

    def test_non_integer_raises(self):
        from attributes import Limit

        with pytest.raises(ValidationError, match="integer"):
            Limit("abc")
        with pytest.raises(ValidationError, match="integer"):
            Limit([])


class TestWork:
    """Test Work (unit of work, non-negative int, supports += 1)."""

    def test_zero(self):
        from attributes import Work

        w = Work(0)
        assert w == 0

    def test_positive(self):
        from attributes import Work

        assert Work(1) == 1
        assert Work(10) == 10

    def test_negative_raises(self):
        from attributes import Work

        with pytest.raises(ValidationError, match=">= 0"):
            Work(-1)

    def test_non_integer_raises(self):
        from attributes import Work

        with pytest.raises(ValidationError, match="integer"):
            Work("x")

    def test_add_one(self):
        from attributes import Work

        w = Work(0)
        w2 = w + 1
        assert w2 == 1
        assert type(w2).__name__ == "Work"


class TestAttributesGetAttr:
    """Test that attributes does not expose geometry types (they live in geometry package)."""

    def test_getattr_point_raises(self):
        import attributes

        with pytest.raises(AttributeError, match="no attribute"):
            getattr(attributes, "Point")

    def test_getattr_unknown_raises(self):
        import attributes

        with pytest.raises(AttributeError, match="no attribute"):
            getattr(attributes, "NoSuchAttribute")


class TestEmail:
    """Test Email attribute."""

    def test_valid(self):
        assert Email("user@example.com") == "user@example.com"

    def test_none_raises(self):
        with pytest.raises(ValidationError, match="required"):
            Email(None)

    def test_non_string_raises(self):
        with pytest.raises(ValidationError, match="string"):
            Email(123)

    def test_empty_raises(self):
        with pytest.raises(ValidationError, match="non-empty"):
            Email("   ")

    def test_invalid_format_raises(self):
        with pytest.raises(ValidationError, match="valid email"):
            Email("invalid")

    def test_slug_property(self):
        e = Email("user@example.com")
        s = e.slug
        assert isinstance(s, str)
        assert "-" in str(s)


class TestOffset:
    """Test Offset attribute (in attributes package)."""

    def test_valid(self):
        from attributes import Offset

        assert Offset("abc") == "abc"

    def test_non_string_raises(self):
        from attributes import Offset

        with pytest.raises(ValidationError, match="string"):
            Offset(123)


class TestReceiptHandle:
    """Test ReceiptHandle attribute."""

    def test_valid(self):
        assert ReceiptHandle("rh-123") == "rh-123"

    def test_none_raises(self):
        with pytest.raises(ValidationError, match="required"):
            ReceiptHandle(None)

    def test_non_string_raises(self):
        with pytest.raises(ValidationError, match="string"):
            ReceiptHandle(123)

    def test_empty_raises(self):
        with pytest.raises(ValidationError, match="non-empty"):
            ReceiptHandle("   ")


class TestSignature:
    """Test Signature attribute."""

    def test_from_string(self):
        s = Signature("x")
        assert isinstance(s, int)

    def test_none_raises(self):
        with pytest.raises(ValidationError, match="must not be None"):
            Signature(None)

    def test_from_non_string_coerced(self):
        s = Signature([1, 2])
        assert isinstance(s, int)

    def test_empty_string_becomes_sentinel(self):
        s = Signature("")
        assert isinstance(s, int)

    def test_hash_returns_self(self):
        s = Signature("abc")
        assert hash(s) == s or s.__hash__() == s


class TestUrl:
    """Test Url attribute."""

    def test_valid(self):
        assert Url("https://example.com/path") == "https://example.com/path"

    def test_none_raises(self):
        with pytest.raises(ValidationError, match="required"):
            Url(None)

    def test_non_string_raises(self):
        with pytest.raises(ValidationError, match="string"):
            Url(123)

    def test_empty_raises(self):
        with pytest.raises(ValidationError, match="non-empty"):
            Url("   ")

    def test_no_scheme_or_netloc_raises(self):
        with pytest.raises(ValidationError, match="scheme and host"):
            Url("not-a-url")

    def test_invalid_scheme_raises(self):
        with pytest.raises(ValidationError, match="scheme must be one of"):
            Url("gopher://example.com")


class TestDuration:
    """Test Duration attribute (non-negative int, milliseconds)."""

    def test_from_int_zero(self):
        from attributes import Duration

        assert Duration(0) == 0

    def test_from_int_positive(self):
        from attributes import Duration

        assert Duration(1000) == 1000
        assert Duration(50000) == 50000

    def test_from_duration_instance(self):
        from attributes import Duration

        d = Duration(1500)
        assert Duration(d) == 1500

    def test_negative_raises(self):
        from attributes import Duration

        with pytest.raises(ValidationError, match=">= 0"):
            Duration(-1)

    def test_non_int_raises(self):
        from attributes import Duration

        with pytest.raises(ValidationError, match="integer"):
            Duration("x")
        with pytest.raises(ValidationError, match="integer"):
            Duration([])

    def test_from_timestamps(self):
        from attributes import Duration
        from attributes import Timestamp

        started = Timestamp.from_iso("2025-01-01T12:00:00.000000Z")
        finished = Timestamp.from_iso("2025-01-01T12:00:05.000000Z")
        d = Duration.from_timestamps(finished, started)
        assert isinstance(d, int)
        assert d >= 5000  # 5 seconds in ms
        assert d <= 5100

    def test_from_timestamps_reversed_returns_zero(self):
        from attributes import Duration
        from attributes import Timestamp

        started = Timestamp.from_iso("2025-01-01T12:00:05.000000Z")
        finished = Timestamp.from_iso("2025-01-01T12:00:00.000000Z")
        d = Duration.from_timestamps(finished, started)
        assert d == 0


class TestCountdown:
    """Test Countdown attribute."""

    def test_from_int(self):
        from attributes import Countdown

        assert Countdown(1) == 1
        assert Countdown(1000) == 1000

    def test_from_countdown_instance(self):
        from attributes import Countdown

        c = Countdown(100)
        assert Countdown(c) == 100

    def test_non_int_raises(self):
        from attributes import Countdown

        with pytest.raises(ValidationError, match="integer"):
            Countdown("x")

    def test_zero_or_negative_raises(self):
        from attributes import Countdown

        with pytest.raises(ValidationError, match="greater than 0"):
            Countdown(0)
        with pytest.raises(ValidationError, match="greater than 0"):
            Countdown(-1)

    def test_from_datetime(self):
        from datetime import datetime

        from attributes import Countdown

        dt = datetime(2025, 1, 1, 12, 0, 0)
        c = Countdown.from_datetime(dt)
        assert isinstance(c, int)
        assert c > 0

    def test_from_date(self):
        from datetime import date

        from attributes import Countdown

        d = date(2025, 1, 1)
        c = Countdown.from_date(d)
        assert c > 0

    def test_from_timestamp(self):
        from attributes import Countdown
        from attributes import Timestamp

        ts = str.__new__(Timestamp, "2025-01-01 12:00:00")
        c = Countdown.from_timestamp(ts)
        assert c > 0


class TestSlug:
    """Test Slug attribute."""

    def test_valid_normalized(self):
        from attributes import Slug

        assert Slug("User@Example.com") == "user-example-com"
        assert Slug("  hello  world  ") == "hello-world"

    def test_none_raises(self):
        from attributes import Slug

        with pytest.raises(ValidationError, match="required"):
            Slug(None)

    def test_non_string_raises(self):
        from attributes import Slug

        with pytest.raises(ValidationError, match="string"):
            Slug(123)

    def test_empty_raises(self):
        from attributes import Slug

        with pytest.raises(ValidationError, match="non-empty"):
            Slug("   ")

    def test_all_non_alphanumeric_becomes_x(self):
        from attributes import Slug

        assert Slug("---") == "x"


class TestTimestamp:
    """Test Timestamp attribute."""

    def test_none_uses_now(self):
        from attributes import Timestamp

        ts = Timestamp(None)
        assert isinstance(ts, str)
        assert "T" in ts or len(ts) > 0

    def test_from_timestamp_instance(self):
        from attributes import Timestamp

        t1 = Timestamp("2025-01-01T12:00:00.000000Z")
        t2 = Timestamp(t1)
        assert t2 == t1

    def test_from_date(self):
        from datetime import date

        from attributes import Timestamp

        ts = Timestamp(date(2025, 1, 15))
        assert "2025-01-15" in str(ts)

    def test_from_datetime(self):
        from datetime import datetime

        from attributes import Timestamp

        ts = Timestamp(datetime(2025, 1, 1, 12, 0, 0))
        assert "2025-01-01" in str(ts)

    def test_from_iso_string(self):
        from attributes import Timestamp

        ts = Timestamp("2025-01-01T12:00:00.000000Z")
        assert "2025-01-01" in str(ts)

    def test_from_iso_empty_uses_now(self):
        from attributes import Timestamp

        ts = Timestamp.from_iso("   ")
        assert isinstance(ts, str)
        assert "T" in ts

    def test_from_iso_non_string_raises(self):
        from attributes import Timestamp

        with pytest.raises(ValidationError, match="expects a string"):
            Timestamp.from_iso(123)

    def test_from_iso_invalid_raises(self):
        from attributes import Timestamp

        with pytest.raises(ValidationError, match="Invalid ISO"):
            Timestamp.from_iso("not-a-date")

    def test_invalid_type_raises(self):
        from attributes import Timestamp

        with pytest.raises(ValidationError, match="Timestamp must be"):
            Timestamp([])

    def test_to_datetime(self):
        from attributes import Timestamp

        ts = Timestamp("2025-01-01T12:00:00.000000Z")
        dt = ts.to_datetime()
        assert dt.year == 2025 and dt.month == 1 and dt.day == 1

    def test_to_datetime_empty_raises(self):
        from attributes import Timestamp

        empty_ts = str.__new__(Timestamp, "")
        with pytest.raises(ValidationError, match="empty"):
            empty_ts.to_datetime()

    def test_to_datetime_invalid_raises(self):
        from attributes import Timestamp

        invalid_ts = str.__new__(Timestamp, "not-valid-datetime")
        with pytest.raises(ValidationError, match="Invalid date/time"):
            invalid_ts.to_datetime()

    def test_to_date(self):
        from attributes import Timestamp

        ts = Timestamp("2025-01-01T12:00:00.000000Z")
        d = ts.to_date()
        assert d.year == 2025 and d.month == 1 and d.day == 1

    def test_to_iso(self):
        from attributes import Timestamp

        ts = Timestamp("2025-01-01T12:00:00.000000Z")
        assert ts.to_iso() == "2025-01-01T12:00:00.000000Z"
        assert isinstance(ts.to_iso(), str)

    def test_now(self):
        from attributes import Timestamp

        ts = Timestamp.now()
        assert isinstance(ts, str)
        assert "T" in ts
