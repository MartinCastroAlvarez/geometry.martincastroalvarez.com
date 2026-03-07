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

    def test_step_has_work_initialized_to_zero(self):
        from attributes import Work

        job = Job(id=Identifier("j1"), step_name=StepName.VALIDATE_POLYGONS)
        step = ValidationPolygonStep(job=job, user=_user(), state={})
        assert step.work == Work(0)
        assert step.work == 0


def _user():
    return User(email=Email("u@e.com"))


class TestSimpleSteps:
    """Test simple steps that return a fixed dict (steps do not enqueue messages; StartTask does)."""

    def test_stitching_step_run(self):
        # StitchingStep reads from job.stdout (output of validation step).
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.STITCHING,
            stdin={},
            stdout={
                "boundary": [[0, 0], [10, 0], [10, 10], [0, 10]],
                "obstacles": [],
            },
        )
        step = StitchingStep(job=job, user=_user(), state={})
        out = step.run()
        assert "stitched" in out
        assert len(out["stitched"]) == 4
        assert out["stitched"][0] in ([0, 0], ["0", "0"])

    def test_stitching_step_run_with_one_obstacle(self):
        # Boundary [0,0]-[10,0]-[10,10]-[0,10]; obstacle [2,2]-[4,2]-[4,4]-[2,4] inside.
        # StitchingStep reads from job.stdout (output of validation step).
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.STITCHING,
            stdin={},
            stdout={
                "boundary": [[0, 0], [10, 0], [10, 10], [0, 10]],
                "obstacles": [[[2, 2], [4, 2], [4, 4], [2, 4]]],
            },
        )
        step = StitchingStep(job=job, user=_user(), state={})
        out = step.run()
        assert "stitched" in out
        assert "stitches" in out
        assert len(out["stitched"]) > 4
        assert len(out["stitches"]) == 1

    def test_validate_polygons_step_run_success(self):
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.VALIDATE_POLYGONS,
            stdin={"boundary": [[0, 0], [10, 0], [10, 10], [0, 10]], "obstacles": []},
        )
        step = ValidationPolygonStep(job=job, user=_user(), state={})
        out = step.run()
        assert "boundary" in out
        assert "obstacles" in out
        assert len(out["boundary"]) == 4
        assert out["obstacles"] == []

    def test_ear_clipping_step_run(self):
        # Ear clipping reads stitched from job.stdout (from stitching step).
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.EAR_CLIPPING,
            stdin={"boundary": [[0, 0], [10, 0], [10, 10], [0, 10]], "obstacles": []},
            stdout={"stitched": [[0, 0], [10, 0], [10, 10], [0, 10]]},
        )
        step = EarClippingStep(job=job, user=_user(), state={})
        out = step.run()
        assert "ears" in out
        ears_values = list(out["ears"].values()) if isinstance(out["ears"], dict) else out["ears"]
        assert len(ears_values) >= 1
        assert len(ears_values[0]) == 3

    def test_ear_clipping_step_run_pentagon(self):
        pentagon = [[0, 0], [2, 0], [2.5, 1.5], [1, 2.5], [-0.5, 1.5]]
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.EAR_CLIPPING,
            stdin={"boundary": pentagon, "obstacles": []},
            stdout={"stitched": pentagon},
        )
        step = EarClippingStep(job=job, user=_user(), state={})
        out = step.run()
        assert "ears" in out
        ears_values = list(out["ears"].values()) if isinstance(out["ears"], dict) else out["ears"]
        assert len(ears_values) == 3
        for ear in ears_values:
            assert len(ear) == 3

    def test_convex_component_optimization_step_run(self):
        # Convex step reads ears from job.stdout (from ear clipping step).
        stitched = [[0, 0], [10, 0], [10, 10], [0, 10]]
        job_ear = Job(
            id=Identifier("j_ear"),
            step_name=StepName.EAR_CLIPPING,
            stdin={"boundary": stitched, "obstacles": []},
            stdout={"stitched": stitched},
        )
        ear_out = EarClippingStep(job=job_ear, user=_user(), state={}).run()
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION,
            stdin={"boundary": stitched, "obstacles": []},
            stdout={"stitched": stitched, "ears": ear_out["ears"]},
        )
        step = ConvexComponentOptimizationStep(job=job, user=_user(), state={})
        out = step.run()
        assert "convex_components" in out
        assert "adjacency" in out
        assert len(out["convex_components"]) >= 1
        assert isinstance(out["adjacency"], dict)
        for key, value in out["adjacency"].items():
            assert isinstance(key, str)
            assert isinstance(value, list)

    def test_guard_placement_step_run(self):
        # Guard placement reads stitched and convex_components from job.stdout.
        stitched = [[0, 0], [10, 0], [10, 10], [0, 10]]
        job_ear = Job(
            id=Identifier("j_ear"),
            step_name=StepName.EAR_CLIPPING,
            stdin={"boundary": stitched, "obstacles": []},
            stdout={"stitched": stitched},
        )
        ear_out = EarClippingStep(job=job_ear, user=_user(), state={}).run()
        job_convex = Job(
            id=Identifier("j_convex"),
            step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION,
            stdin={"boundary": stitched, "obstacles": []},
            stdout={"stitched": stitched, "ears": ear_out["ears"]},
        )
        convex_out = ConvexComponentOptimizationStep(job=job_convex, user=_user(), state={}).run()
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.GUARD_PLACEMENT,
            stdin={"boundary": stitched, "obstacles": []},
            stdout={
                "boundary": stitched,
                "obstacles": [],
                "stitched": stitched,
                "convex_components": convex_out["convex_components"],
                "adjacency": convex_out["adjacency"],
            },
        )
        step = GuardPlacementStep(job=job, user=_user(), state={})
        out = step.run()
        assert "guards" in out
        assert "visibility" in out
        assert len(out["guards"]) >= 1
        assert len(out["visibility"]) == len(out["guards"])

    def test_guard_placement_step_run_with_one_obstacle(self):
        boundary = [[0, 0], [10, 0], [10, 10], [0, 10]]
        obstacles = [[[2, 2], [4, 2], [4, 4], [2, 4]]]
        # StitchingStep reads from stdout (output of validation step).
        job_stitch = Job(
            id=Identifier("j_stitch"),
            step_name=StepName.STITCHING,
            stdin={},
            stdout={"boundary": boundary, "obstacles": obstacles},
        )
        stitch_out = StitchingStep(job=job_stitch, user=_user(), state={}).run()
        job_ear = Job(
            id=Identifier("j_ear"),
            step_name=StepName.EAR_CLIPPING,
            stdin={"boundary": boundary, "obstacles": obstacles},
            stdout={"stitched": stitch_out["stitched"]},
        )
        ear_out = EarClippingStep(job=job_ear, user=_user(), state={}).run()
        job_convex = Job(
            id=Identifier("j_convex"),
            step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION,
            stdin={"boundary": boundary, "obstacles": obstacles},
            stdout={"stitched": stitch_out["stitched"], "ears": ear_out["ears"]},
        )
        convex_out = ConvexComponentOptimizationStep(job=job_convex, user=_user(), state={}).run()
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.GUARD_PLACEMENT,
            stdin={"boundary": boundary, "obstacles": obstacles},
            stdout={
                "boundary": boundary,
                "obstacles": obstacles,
                "stitched": stitch_out["stitched"],
                "convex_components": convex_out["convex_components"],
                "adjacency": convex_out["adjacency"],
            },
        )
        step = GuardPlacementStep(job=job, user=_user(), state={})
        out = step.run()
        assert "guards" in out
        assert "visibility" in out
        assert len(out["guards"]) >= 1
        assert len(out["visibility"]) == len(out["guards"])


class TestArtGalleryStep:
    """Test ArtGalleryStep with mocks (step does not enqueue; StartTask.broadcast/report do)."""

    @patch("steps.JobsRepository")
    def test_art_gallery_step_run_creates_children_and_puts_report(self, mock_repo_cls):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_repo.exists.return_value = False

        job = Job(id=Identifier("parent-1"), step_name=StepName.ART_GALLERY, stdin={"boundary": []})
        step = ArtGalleryStep(job=job, user=_user(), state={})

        out = step.run()

        assert out.get("boundary") == []
        assert len(job.children_ids) == 5
        mock_repo.save.assert_called()

    @patch("steps.JobsRepository")
    def test_art_gallery_step_run_existing_children_skips_create(self, mock_repo_cls):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_repo.exists.return_value = True

        job = Job(id=Identifier("parent-1"), step_name=StepName.ART_GALLERY, stdin={})
        step = ArtGalleryStep(job=job, user=_user(), state={})

        out = step.run()

        assert out == {"boundary": None, "obstacles": None}
        mock_repo.save.assert_not_called()
