"""
Test that api/steps.py runs the full pipeline for the palace polygon (boundary + 8 obstacles).
Expects 23 guards for sufficient coverage.
"""

from attributes import Email
from attributes import Identifier
from enums import StepName
from models import Job
from models import User
from tests.utils import assert_convex_components_simple_convex_no_obstacle_intersection
from tests.utils import assert_convex_components_visibility_within_component
from tests.utils import assert_ears_no_obstacle_intersection
from tests.utils import assert_ears_simple_and_convex
from steps import ConvexComponentOptimizationStep
from steps import EarClippingStep
from steps import GuardPlacementStep
from steps import StitchingStep
from steps import ValidationPolygonStep


def _user():
    return User(email=Email("u@e.com"))


PALACE_STDIN = {
    "boundary": [
        ["284.1519085825432", "19.5"],
        ["286.15297836129355", "34.5"],
        ["392.20967663505957", "35.5"],
        ["393.2102115244347", "16.5"],
        ["450.2407002188184", "15.5"],
        ["452.2417699975687", "87.5"],
        ["397.21235108193537", "86.5"],
        ["397.21235108193537", "71.5"],
        ["378.20218818380744", "71.5"],
        ["380.20325796255776", "177.5"],
        ["486.2599562363239", "179.5"],
        ["486.2599562363239", "160.5"],
        ["469.2508631169463", "160.5"],
        ["469.2508631169463", "108.5"],
        ["543.2904449307075", "108.5"],
        ["540.2888402625821", "162.5"],
        ["523.2797471432045", "162.5"],
        ["524.2802820325796", "268.5"],
        ["541.2893751519572", "267.5"],
        ["541.2893751519572", "324.5"],
        ["473.2530026744469", "324.5"],
        ["472.25246778507176", "270.5"],
        ["489.2615609044493", "269.5"],
        ["488.26102601507415", "250.5"],
        ["379.2027230731826", "252.5"],
        ["379.2027230731826", "359.5"],
        ["398.21288597131047", "357.5"],
        ["398.21288597131047", "343.5"],
        ["451.24123510819356", "342.5"],
        ["454.242839776319", "412.5"],
        ["397.21235108193537", "413.5"],
        ["397.21235108193537", "398.5"],
        ["290.1551179187941", "399.5"],
        ["290.1551179187941", "414.5"],
        ["232.12409433503524", "415.5"],
        ["232.12409433503527", "344.5"],
        ["287.15351325066865", "343.5"],
        ["289.1545830294189", "360.5"],
        ["305.16314125942137", "360.5"],
        ["306.1636761487965", "252.5"],
        ["199.10644298565524", "251.5"],
        ["199.10644298565524", "270.5"],
        ["216.11553610503285", "270.5"],
        ["215.11500121565768", "323.5"],
        ["145.07755895939704", "324.5"],
        ["144.85521772622718", "269.2777777590148"],
        ["160.08558230002433", "268.5"],
        ["163.08718696814978", "164.5"],
        ["144.07702407002188", "162.5"],
        ["144.07702407002188", "111.5"],
        ["211.11286165815707", "109.5"],
        ["214.11446632628252", "162.5"],
        ["197.10537320690494", "162.5"],
        ["197.10537320690494", "179.5"],
        ["305.16314125942137", "178.5"],
        ["305.16314125942137", "70.5"],
        ["289.1545830294189", "70.5"],
        ["289.1545830294189", "90.5"],
        ["237.126768781911", "91.5"],
        ["235.12569900316072", "20.5"],
    ],
    "obstacles": [
        [
            ["243.8112833585848", "357.29166510699565"],
            ["245.20091507606259", "398.26388705246427"],
            ["276.467628719313", "397.56944261271053"],
            ["276.467628719313", "357.29166510699565"],
        ],
        [
            ["409.8421890393306", "73.95833283846028"],
            ["437.6348233888865", "73.95833283846028"],
            ["436.24519167140875", "28.12499981471578"],
            ["409.1473731805917", "28.81944425446948"],
        ],
        [
            ["412.4268309680239", "399.65277593197163"],
            ["441.8338030991706", "400.34722037172537"],
            ["437.66490794673723", "354.51388734798087"],
            ["411.956721173398", "355.20833178773455"],
        ],
        [
            ["484.18748592439266", "148.95833233186042"],
            ["526.5712533074654", "149.6527767716141"],
            ["527.9608850249433", "121.87499918146591"],
            ["484.18748592439266", "121.5617603309473"],
        ],
        [
            ["486.27193350060935", "311.4583312342273"],
            ["527.9608850249433", "311.4583312342273"],
            ["527.9608850249433", "283.6805536440791"],
            ["485.5771176418705", "284.3749980838328"],
        ],
        [
            ["273.7574483431257", "35.069444207562086"],
            ["248.04926156978647", "33.68055532805468"],
            ["248.74407742852537", "74.65277727352326"],
            ["275.14708006060346", "74.65277727352326"],
        ],
        [
            ["160.50246336868537", "309.37499791027545"],
            ["200.10696731680252", "308.6805534705217"],
            ["200.10696731680252", "284.28634539259923"],
            ["161.19727922742425", "285.7638869586495"],
        ],
        [
            ["160.50246336868537", "151.04166564643077"],
            ["198.71733559932474", "149.65277676692335"],
            ["198.02251974058584", "124.65277693578999"],
            ["161.19727922742425", "126.04166581529739"],
        ],
    ],
}


def test_palace_full_pipeline_requires_twenty_three_guards():
    """Run full pipeline for palace polygon; expect 23 guards for sufficient coverage."""
    stdout = {}
    job_validate = Job(
        id=Identifier("palace-v"),
        step_name=StepName.VALIDATE_POLYGONS,
        stdin=dict(PALACE_STDIN),
    )
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user()).run())
    job_stitch = Job(
        id=Identifier("palace-s"),
        step_name=StepName.STITCHING,
        stdin=dict(PALACE_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(StitchingStep(job=job_stitch, user=_user()).run())
    job_ear = Job(
        id=Identifier("palace-e"),
        step_name=StepName.EAR_CLIPPING,
        stdin=dict(PALACE_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(EarClippingStep(job=job_ear, user=_user()).run())
    assert_ears_simple_and_convex(stdout["ears"])
    assert_ears_no_obstacle_intersection(stdout["ears"], stdout["obstacles"])
    job_convex = Job(
        id=Identifier("palace-c"),
        step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION,
        stdin=dict(PALACE_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(ConvexComponentOptimizationStep(job=job_convex, user=_user()).run())

    assert_convex_components_simple_convex_no_obstacle_intersection(
        stdout["convex_components"], stdout["obstacles"]
    )
    assert_convex_components_visibility_within_component(
        stdout["convex_components"], stdout["obstacles"]
    )

    job_guard = Job(
        id=Identifier("palace-g"),
        step_name=StepName.GUARD_PLACEMENT,
        stdin=dict(PALACE_STDIN),
        stdout=dict(stdout),
    )
    guard_out = GuardPlacementStep(job=job_guard, user=_user()).run()
    assert len(guard_out["guards"]) == 24, (
        f"Palace gallery expects 24 guards; got {len(guard_out['guards'])}"
    )
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
