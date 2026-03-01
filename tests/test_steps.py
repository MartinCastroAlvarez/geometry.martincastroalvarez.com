"""Tests for steps package."""

from unittest.mock import MagicMock
from unittest.mock import patch

from attributes import Email
from attributes import Identifier
from enums import StepName
from models import Job
from models import User
from steps import ArtGalleryStep
from steps import ConvexComponentOptimizationStep
from steps import EarClippingStep
from steps import GuardPlacementStep
from steps import Step
from steps import StitchingStep
from steps import ValidationPolygonStep
from tasks import StartTask


class TestStepRegistration:
    """Test Step.of() maps step_name to the correct step class."""

    def test_step_class_by_name_has_art_gallery(self):
        assert Step.of(StepName.ART_GALLERY) is ArtGalleryStep

    def test_step_class_by_name_has_validate_polygons(self):
        assert Step.of(StepName.VALIDATE_POLYGONS) is ValidationPolygonStep


def _user():
    return User(email=Email("u@e.com"))


class TestSimpleSteps:
    """Test simple steps that return a fixed dict (steps do not enqueue messages; StartTask does)."""

    def test_stitching_step_run(self):
        job = Job(id=Identifier("j1"), step_name=StepName.STITCHING)
        step = StitchingStep(job=job, user=_user())
        out = step.run()
        assert out == {"step:stitching": "success"}

    def test_validate_polygons_step_run_success(self):
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.VALIDATE_POLYGONS,
            stdin={"boundary": [[0, 0], [10, 0], [10, 10], [0, 10]], "obstacles": []},
        )
        step = ValidationPolygonStep(job=job, user=_user())
        out = step.run()
        assert out == {"step:validate_polygons": "success"}

    def test_ear_clipping_step_run(self):
        job = Job(id=Identifier("j1"), step_name=StepName.EAR_CLIPPING)
        step = EarClippingStep(job=job, user=_user())
        assert step.run() == {"step:ear_clipping": "success"}

    def test_convex_component_optimization_step_run(self):
        job = Job(id=Identifier("j1"), step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION)
        step = ConvexComponentOptimizationStep(job=job, user=_user())
        assert step.run() == {"step:convex_component_optimization": "success"}

    def test_guard_placement_step_run(self):
        job = Job(id=Identifier("j1"), step_name=StepName.GUARD_PLACEMENT)
        step = GuardPlacementStep(job=job, user=_user())
        assert step.run() == {"step:guard_placement": "success"}


class TestArtGalleryStep:
    """Test ArtGalleryStep with mocks (step does not enqueue; StartTask.broadcast/report do)."""

    @patch("steps.JobsRepository")
    def test_art_gallery_step_run_creates_children_and_puts_report(self, mock_repo_cls):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_repo.exists.return_value = False

        job = Job(id=Identifier("parent-1"), step_name=StepName.ART_GALLERY, stdin={"boundary": []})
        step = ArtGalleryStep(job=job, user=_user())

        out = step.run()

        assert out["step:art_gallery"] == "success"
        assert out.get("boundary") == []
        assert len(job.children_ids) == 5
        mock_repo.save.assert_called()

    @patch("steps.JobsRepository")
    def test_art_gallery_step_run_existing_children_skips_create(self, mock_repo_cls):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_repo.exists.return_value = True

        job = Job(id=Identifier("parent-1"), step_name=StepName.ART_GALLERY, stdin={})
        step = ArtGalleryStep(job=job, user=_user())

        out = step.run()

        assert out == {"step:art_gallery": "success", "boundary": None, "obstacles": None}
        mock_repo.save.assert_not_called()
