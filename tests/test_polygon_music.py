"""
Test that api/steps.py runs the full pipeline for the music polygon (boundary + obstacles).
Expects 12 guards for sufficient coverage (current pipeline result).
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
from tests.utils import print_guard_coverage_report
from steps import ConvexComponentOptimizationStep
from steps import EarClippingStep
from steps import GuardPlacementStep
from steps import StitchingStep
from steps import ValidationPolygonStep


def _user():
    return User(email=Email("u@e.com"))


POLYGON_MUSIC_STDIN = {
    "boundary": [
        ["26.195704333568926", "644.1609435193916"],
        ["138.99809963585943", "288.3631044677508"],
        ["120.94077315827863", "234.32342863840412"],
        ["95.73873085339167", "160.05199265728083"],
        ["92.13960612691469", "110.88453046452742"],
        ["117.35211176285213", "88.07974671723338"],
        ["153.35152824717014", "95.11220315941769"],
        ["182.63420864723355", "94.82221124482236"],
        ["197.56376217508253", "76.01029826617508"],
        ["207.59883829518293", "63.41138041652077"],
        ["210.89371461011666", "69.31527899525283"],
        ["270.5320784407838", "68.15787157937605"],
        ["264.16293278896495", "64.68564933174564"],
        ["220.48131448555412", "63.92977747884254"],
        ["227.67024766320898", "-334.2067456429657"],
        ["273.31505851704605", "-334.79999999999995"],
        ["275.6958424507659", "68.72660305862331"],
        ["285.293508388038", "77.12104782323979"],
        ["303.2882567469002", "68.91230664144518"],
        ["397.90217305972675", "-26.634152577490177"],
        ["433.87478777389896", "-61.59859552556405"],
        ["448.2128638188152", "-63.733146449741184"],
        ["459.0581975281875", "-56.853323310593495"],
        ["463.4693216519212", "-32.45693126018734"],
        ["373.53301686297226", "299.69523394627817"],
        ["437.9776025374396", "475.22663816179585"],
        ["334.4751276440554", "547.3804779905009"],
    ],
    "obstacles": [
        [
            ["201.60118552151243", "402.0245023481045"],
            ["298.37851178461784", "400.82926840182625"],
            ["300.811045905586", "362.150802768234"],
            ["205.01660018724368", "363.21633466053805"],
        ],
        [
            ["220.54117961831585", "131.80663566137017"],
            ["277.0193730537644", "132.38263562551361"],
            ["277.01937305376447", "113.37463680878045"],
            ["221.11748771459597", "112.79863684463702"],
        ],
        [
            ["217.65963913691542", "187.6786321832827"],
            ["277.01937305376447", "187.67863218328276"],
            ["277.0193730537644", "169.82263329483644"],
            ["219.3885634257557", "170.9746332231233"],
        ],
        [
            ["316.6611844856395", "504.1774609030218"],
            ["331.54914363954185", "503.6174606415676"],
            ["335.84406802563467", "492.21744635496293"],
            ["333.44278429113433", "482.6174463549629"],
            ["324.74550639179085", "480.81745914754356"],
            ["315.2204142449393", "481.0574588860894"],
            ["311.03080276913096", "492.6174463549629"],
        ],
        [
            ["340.19376508374313", "460.89745731736417"],
            ["354.12121074384527", "461.3774573547148"],
            ["360.65733328213844", "451.81744635496295"],
            ["356.5224944783456", "440.737455748639"],
            ["342.11479207134346", "441.21745578598956"],
            ["336.6444959371348", "451.0174463549629"],
        ],
        [
            ["361.0849335738963", "419.13745406786194"],
            ["372.6911382906481", "420.09745414256315"],
            ["378.29413367114887", "408.89745283529214"],
            ["373.81173736674816", "401.2974528352921"],
            ["365.4599007511392", "400.21744635496293"],
            ["357.0554076803878", "408.617446354963"],
        ],
        [
            ["229.23333104308415", "-143.87282242281773"],
            ["272.85399560093714", "-144.35723736793213"],
            ["269.94595129708034", "-148.7169718739616"],
            ["228.74865699244134", "-148.23255692884723"],
        ],
        [
            ["231.16865895792372", "-217.01948116087138"],
            ["270.4272570599915", "-217.0194811608714"],
            ["270.42725705999146", "-221.37921566690085"],
            ["229.2299627553525", "-220.89480072178645"],
        ],
        [
            ["229.22996275535246", "-284.35315853177104"],
            ["270.9119311106343", "-285.80640336711417"],
            ["269.45790895870584", "-288.7128930378004"],
            ["229.7146368059953", "-288.2284780926861"],
        ],
        [
            ["227.7793088911557", "-0.9704136140739479"],
            ["269.4612772464375", "-1.4548285591883143"],
            ["270.4306253477231", "-4.845733174989022"],
            ["226.80996078987008", "-3.876903284760232"],
        ],
        [
            ["270.91529939836596", "-71.69499560077423"],
            ["271.3999734490087", "-74.60148527146056"],
            ["225.35593863794165", "-75.08590021657494"],
            ["226.32528673922727", "-72.17941054588866"],
        ],
    ],
}


def test_music_full_pipeline_requires_twelve_guards():
    stdout = {}
    job_validate = Job(
        id=Identifier("music-v"),
        step_name=StepName.VALIDATE_POLYGONS,
        stdin=dict(POLYGON_MUSIC_STDIN),
    )
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user(), state={}).run())
    job_stitch = Job(
        id=Identifier("music-s"),
        step_name=StepName.STITCHING,
        stdin=dict(POLYGON_MUSIC_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(StitchingStep(job=job_stitch, user=_user(), state={}).run())
    job_ear = Job(
        id=Identifier("music-e"),
        step_name=StepName.EAR_CLIPPING,
        stdin=dict(POLYGON_MUSIC_STDIN),
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
        id=Identifier("music-c"),
        step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION,
        stdin=dict(POLYGON_MUSIC_STDIN),
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
        id=Identifier("music-g"),
        step_name=StepName.GUARD_PLACEMENT,
        stdin=dict(POLYGON_MUSIC_STDIN),
        stdout=dict(stdout),
    )
    guard_out = GuardPlacementStep(job=job_guard, user=_user(), state={}).run()
    assert len(guard_out["guards"]) == 12, (
        f"Music gallery expects 12 guards; got {len(guard_out['guards'])}"
    )
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
    assert_no_redundant_guards(guard_out)
    print_guard_coverage_report(guard_out, "Music guard coverage report")
