"""
Test that api/steps.py runs the full pipeline for the Wuhan polygon (boundary only, no obstacles).
Expects 7 guards for sufficient coverage (with stitch-edge non-intersection).
"""

from attributes import Email
from attributes import Identifier
from enums import StepName
from exceptions import SuspendedStepError
from geometry import ConvexComponent
from geometry import Ear
from geometry import Polygon
from models import Job
from models import User
from tests.utils import assert_convex_components_visibility_within_component
from tests.utils import assert_ears_simple_and_convex
from tests.utils import assert_no_redundant_guards
from tests.utils import assert_no_stitches_share_a_point
from tests.utils import print_guard_coverage_report
from steps import ConvexComponentOptimizationStep
from steps import EarClippingStep
from steps import GuardPlacementStep
from steps import StitchingStep
from steps import ValidationPolygonStep


def _user():
    return User(email=Email("u@e.com"))


POLYGON_WUHAN_STDIN = {
    "boundary": [
        ["251.13425723316314", "176.5"],
        ["250.133722343788", "109.5"],
        ["271.1449550206662", "159.5"],
        ["287.15351325066865", "147.5"],
        ["306.1636761487965", "146.5"],
        ["325.1738390469244", "160.5"],
        ["340.1818623875517", "108.5"],
        ["345.18453683442743", "177.5"],
        ["345.18453683442743", "197.5"],
        ["339.18132749817653", "215.5"],
        ["414.2214442013129", "214.5"],
        ["471.2519328956966", "197.5"],
        ["520.278142475079", "163.5"],
        ["541.2893751519572", "125.5"],
        ["575.3075613907124", "160.5"],
        ["593.3171893994652", "195.5"],
        ["621.9250182348652", "247.5"],
        ["642.1348893751519", "358.3007936050548"],
        ["606.2252370532458", "328.3988211186096"],
        ["576.2325309992706", "327.19961472366435"],
        ["554.6377826404084", "349.98453622762327"],
        ["540.2412837345004", "321.20358274893835"],
        ["492.25295404814005", "304.4146932197055"],
        ["443.06491611962076", "320.00437635399317"],
        ["420.2704595185995", "341.59009146300684"],
        ["398.67571115973743", "321.20358274893835"],
        ["339.89000729394604", "306.81310600959586"],
        ["305.0984682713348", "379.9646961012535"],
        ["265.50809628008756", "305.6138996146507"],
        ["210.32151714077315", "328.3988211186096"],
        ["192.32589350838805", "347.58612343773285"],
        ["169.53143690736692", "326.0004083287192"],
        ["125.14223194748358", "312.8091379843219"],
        ["81.95273522975931", "328.3988211186096"],
        ["61.55769511305617", "351.1837426225685"],
        ["39.96294675419402", "324.801201933774"],
        ["17.16849015317287", "327.19961472366435"],
        ["-21.397422805737897", "357.5"],
        ["-11.186092876246043", "259.8944447646164"],
        ["4.4144906394359325", "194.5"],
        ["22.623292000972533", "160.6992063949452"],
        ["52.644006807682956", "124.5"],
        ["76.65217602723074", "159.3007936050548"],
        ["128.08247021638704", "195.5"],
        ["191.9081935327012", "213.5"],
        ["261.13960612691466", "214.5"],
        ["252.1347921225383", "196.5"],
    ],
    "obstacles": [],
}


def test_wuhan_full_pipeline_requires_seven_guards():
    """Run full pipeline for Wuhan polygon; expect 7 guards for sufficient coverage."""
    stdout = {}
    job_validate = Job(
        id=Identifier("wuhan-v"),
        step_name=StepName.VALIDATE_POLYGONS,
        stdin=dict(POLYGON_WUHAN_STDIN),
    )
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user(), state={}).run())
    job_stitch = Job(
        id=Identifier("wuhan-s"),
        step_name=StepName.STITCHING,
        stdin=dict(POLYGON_WUHAN_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(StitchingStep(job=job_stitch, user=_user(), state={}).run())
    assert_no_stitches_share_a_point(stdout["stitches"])
    job_ear = Job(
        id=Identifier("wuhan-e"),
        step_name=StepName.EAR_CLIPPING,
        stdin=dict(POLYGON_WUHAN_STDIN),
        stdout=dict(stdout),
    )
    state = {}
    while True:
        step = EarClippingStep(job=job_ear, user=_user(), state=state)
        try:
            stdout.update(step.run())
            break
        except SuspendedStepError as e:
            state = e.state
    assert_ears_simple_and_convex(stdout["ears"])

    stitched_points = set(Polygon.unserialize(stdout["stitched"]))
    ears_points = set()
    for ear_ser in stdout["ears"].values():
        ear = Ear.unserialize(ear_ser)
        ears_points.update(ear)
    assert stitched_points == ears_points, (
        f"Ears' vertices must equal stitched vertices. "
        f"Only in stitched: {stitched_points - ears_points}. "
        f"Only in ears: {ears_points - stitched_points}."
    )

    job_convex = Job(
        id=Identifier("wuhan-c"),
        step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION,
        stdin=dict(POLYGON_WUHAN_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(ConvexComponentOptimizationStep(job=job_convex, user=_user(), state={}).run())

    assert_convex_components_visibility_within_component(
        stdout["convex_components"], stdout["obstacles"]
    )

    stitched_points = set(Polygon.unserialize(stdout["stitched"]))
    component_points = set()
    for comp_ser in stdout["convex_components"].values():
        comp = ConvexComponent.unserialize(comp_ser)
        component_points.update(comp)
    assert stitched_points == component_points, (
        f"Convex components' vertices must equal stitched vertices. "
        f"Only in stitched: {stitched_points - component_points}. "
        f"Only in components: {component_points - stitched_points}."
    )

    job_guard = Job(
        id=Identifier("wuhan-g"),
        step_name=StepName.GUARD_PLACEMENT,
        stdin=dict(POLYGON_WUHAN_STDIN),
        stdout=dict(stdout),
    )
    guard_out = GuardPlacementStep(job=job_guard, user=_user(), state={}).run()
    assert len(guard_out["guards"]) == 5, (
        f"Wuhan gallery expects 5 guards; got {len(guard_out['guards'])}"
    )
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
    assert_no_redundant_guards(guard_out)
    print_guard_coverage_report(guard_out, "Wuhan guard coverage report")
