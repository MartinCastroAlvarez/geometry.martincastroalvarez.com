"""Tests for serializers module (TypedDict shapes and coverage in ArtGalleryDict)."""

from geometry import Point
from models import ArtGallery
from serializers import ArtGalleryDict


def test_art_gallery_serialize_includes_coverage():
    """ArtGallery.serialize() must include coverage (list of serialized points)."""
    from attributes import Identifier
    from geometry import Polygon

    boundary = Polygon.unserialize([[0, 0], [2, 0], [2, 2], [0, 2]])
    gallery = ArtGallery(
        id=Identifier("g1"),
        boundary=boundary,
        owner_job_id=Identifier("j1"),
        title="Test",
        coverage={Point([0, 0]), Point([1, 1])},
    )
    out: ArtGalleryDict = gallery.serialize()
    assert "coverage" in out
    assert isinstance(out["coverage"], list)
    assert len(out["coverage"]) == 2
