"""Tests for indexes package."""

from indexes.gallery import ArtGalleryPublicIndex


class TestArtGalleryPublicIndex:
    """Test ArtGalleryPublicIndex."""

    def test_index_path(self):
        idx = ArtGalleryPublicIndex()
        assert idx.path == "index/galleries/"
        assert idx.NAME == "galleries"
