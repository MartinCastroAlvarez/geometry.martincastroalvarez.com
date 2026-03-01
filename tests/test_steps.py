"""Tests for steps package."""

from unittest.mock import MagicMock
from unittest.mock import patch

from attributes import Email
from attributes import Identifier
from enums import StepName
from models import Job
from steps import ArtGalleryStep
from tasks import StartTask
from steps import ConvexComponentOptimizationStep
from steps import EarClippingStep
from steps import GuardPlacementStep
from steps import StitchingStep
from steps import VisibilityMatrixStep


class TestStepRegistration:
    """Test step registration in StartTask.STEP_CLASS_BY_NAME."""

    def test_step_class_by_name_has_art_gallery(self):
        assert StepName.ART_GALLERY in StartTask.STEP_CLASS_BY_NAME
        assert StartTask.STEP_CLASS_BY_NAME[StepName.ART_GALLERY] is ArtGalleryStep

    def test_step_class_by_name_has_visibility_matrix(self):
        assert StepName.VISIBILITY_MATRIX in StartTask.STEP_CLASS_BY_NAME
        assert StartTask.STEP_CLASS_BY_NAME[StepName.VISIBILITY_MATRIX] is VisibilityMatrixStep


class TestSimpleSteps:
    """Test simple steps that return a fixed dict."""

    def test_visibility_matrix_step_run(self):
        job = Job(id=Identifier("j1"), step_name=StepName.VISIBILITY_MATRIX)
        step = VisibilityMatrixStep(job=job, user_email=Email("u@e.com"))
        out = step.run()
        assert out == {"step:visibility_matrix": "success"}

    def test_stitching_step_run(self):
        job = Job(id=Identifier("j1"), step_name=StepName.STITCHING)
        step = StitchingStep(job=job, user_email=Email("u@e.com"))
        assert step.run() == {"step:stitching": "success"}

    def test_ear_clipping_step_run(self):
        job = Job(id=Identifier("j1"), step_name=StepName.EAR_CLIPPING)
        step = EarClippingStep(job=job, user_email=Email("u@e.com"))
        assert step.run() == {"step:ear_clipping": "success"}

    def test_convex_component_optimization_step_run(self):
        job = Job(id=Identifier("j1"), step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION)
        step = ConvexComponentOptimizationStep(job=job, user_email=Email("u@e.com"))
        assert step.run() == {"step:convex_component_optimization": "success"}

    def test_guard_placement_step_run(self):
        job = Job(id=Identifier("j1"), step_name=StepName.GUARD_PLACEMENT)
        step = GuardPlacementStep(job=job, user_email=Email("u@e.com"))
        assert step.run() == {"step:guard_placement": "success"}


class TestArtGalleryStep:
    """Test ArtGalleryStep with mocks."""

    @patch("steps.Queue")
    @patch("steps.JobsRepository")
    def test_art_gallery_step_run_creates_children_and_puts_report(self, mock_repo_cls, mock_queue_cls):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_repo.exists.return_value = False
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue

        job = Job(id=Identifier("parent-1"), step_name=StepName.ART_GALLERY, stdin={"boundary": []})
        step = ArtGalleryStep(job=job, user_email=Email("u@e.com"))

        out = step.run()

        assert out == {"step:art_gallery": "success"}
        assert len(job.children_ids) == 5
        mock_repo.save.assert_called()
        mock_queue.put.assert_called_once()

    @patch("steps.Queue")
    @patch("steps.JobsRepository")
    def test_art_gallery_step_run_existing_children_skips_create(self, mock_repo_cls, mock_queue_cls):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue

        job = Job(id=Identifier("parent-1"), step_name=StepName.ART_GALLERY, stdin={})
        step = ArtGalleryStep(job=job, user_email=Email("u@e.com"))

        out = step.run()

        assert out == {"step:art_gallery": "success"}
        mock_repo.save.assert_not_called()
        mock_queue.put.assert_called_once()
