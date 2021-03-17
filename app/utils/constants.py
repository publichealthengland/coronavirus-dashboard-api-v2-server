#!/usr/bin python3

# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python:
from pathlib import Path
from os import getenv
from typing import NamedTuple, Dict, List, Callable, Any
from string import Template
from datetime import datetime
import re

# 3rd party:

# Internal: 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'DBQueries',
    'DATA_TYPES',
    'ENVIRONMENT',
    'BASE_DIR'
    # 'RequestMethod'
]


ENVIRONMENT = getenv("ENVIRONMENT", "PRODUCTION")

BASE_DIR = Path(__file__).resolve().parent.parent


def to_template(text: str) -> Template:
    return Template(re.sub(r"[\n\t\s]+", " ", text, flags=re.MULTILINE))


class DBQueries(NamedTuple):
    # noinspection SqlResolve,SqlNoDataSourceInspection
    main_data = to_template("""\
SELECT
    ar.area_type  AS "areaType",
    area_code     AS "areaCode",
    area_name     AS "areaName",
    date::VARCHAR AS date,
    metric,
    CASE
        WHEN (payload ? 'value') THEN (payload -> 'value')
        ELSE payload::JSONB
    END AS value
FROM covid19.time_series_p${partition} AS ts
    JOIN covid19.metric_reference  AS mr  ON mr.id = metric_id
    JOIN covid19.release_reference AS rr  ON rr.id = release_id
    JOIN covid19.area_reference    AS ar  ON ar.id = area_id
WHERE
      metric = ANY($$1::VARCHAR[])
  AND rr.released IS TRUE
  AND ar.area_type = $$2
  $filters
ORDER BY area_code, date DESC""")

    nested_object = to_template("""\
SELECT
    ar.area_type                                                     AS "areaType",
    area_code                                                        AS "areaCode",
    area_name                                                        AS "areaName",
    date::VARCHAR                                                    AS date,
    mr.metric || UPPER(LEFT(ts_obj.key, 1)) || RIGHT(ts_obj.key, -1) AS metric,
    ts_obj.value                                                     AS value
FROM covid19.time_series_p${partition} AS ts
    JOIN covid19.metric_reference  AS mr  ON mr.id = metric_id
    JOIN covid19.release_reference AS rr  ON rr.id = release_id
    JOIN covid19.area_reference    AS ar  ON ar.id = area_id,
JSONB_EACH(payload) AS ts_obj
WHERE
       mr.metric || UPPER(LEFT(ts_obj.key, 1)) || RIGHT(ts_obj.key, -1) = ANY($$1::VARCHAR[])
  AND rr.released IS TRUE
  AND ar.area_type = $$2
  $filters
ORDER BY area_code, date DESC""")

    nested_array = to_template("""\
SELECT
    ar.area_type  AS "areaType",
    area_code     AS "areaCode",
    area_name     AS "areaName",
    date::VARCHAR AS date,
    metric,
    payload       AS "${metric_name}"
FROM covid19.time_series_p${partition} AS ts
    JOIN covid19.metric_reference   AS mr  ON mr.id = metric_id
    JOIN covid19.release_reference  AS rr  ON rr.id = release_id
    JOIN covid19.area_reference     AS ar  ON ar.id = area_id
WHERE
      metric = ANY($$1::VARCHAR[])
  AND rr.released IS TRUE
  AND ar.area_type = $$2
  $filters
ORDER BY area_code, date DESC""")

    # noinspection SqlResolve,SqlNoDataSourceInspection
    exists = to_template("""\
SELECT
    area_code     AS "areaCode"
FROM covid19.time_series_p${partition} AS ts
    JOIN covid19.metric_reference  AS mr  ON mr.id = metric_id
    JOIN covid19.release_reference AS rr  ON rr.id = release_id
    JOIN covid19.area_reference    AS ar  ON ar.id = area_id
WHERE
      metric = ANY($$1::VARCHAR[])
  AND rr.released IS TRUE
  AND ar.area_type = $$2
  $filters
FETCH FIRST 1 ROW ONLY""")


DATA_TYPES: Dict[str, Callable[[str], Any]] = {
    'hash': str,
    'areaType': str,
    'date': datetime,
    'areaName': str,
    'areaNameLower': str,
    'areaCode': str,
    'covidOccupiedMVBeds': int,
    'cumAdmissions': int,
    'cumCasesByPublishDate': int,
    'cumPillarFourTestsByPublishDate': int,
    'cumPillarOneTestsByPublishDate': int,
    'cumPillarThreeTestsByPublishDate': int,
    'cumPillarTwoTestsByPublishDate': int,
    'cumTestsByPublishDate': int,
    'hospitalCases': int,
    'newAdmissions': int,
    'newCasesByPublishDate': int,
    'newPillarFourTestsByPublishDate': int,
    'newPillarOneTestsByPublishDate': int,
    'newPillarThreeTestsByPublishDate': int,
    'newPillarTwoTestsByPublishDate': int,
    'newTestsByPublishDate': int,
    'plannedCapacityByPublishDate': int,
    'newCasesBySpecimenDate': int,
    'cumCasesBySpecimenDate': int,
    'maleCases': list,
    'femaleCases': list,
    'cumAdmissionsByAge': list,

    "femaleDeaths28Days": int,
    "maleDeaths28Days": int,

    'changeInNewCasesBySpecimenDate': int,
    'previouslyReportedNewCasesBySpecimenDate': int,

    "cumCasesBySpecimenDateRate": float,
    'cumCasesByPublishDateRate': float,

    'release': datetime,

    "newDeathsByDeathDate": int,
    "newDeathsByDeathDateRate": float,
    'newDeathsByDeathDateRollingRate': float,
    'newDeathsByDeathDateRollingSum': int,
    "cumDeathsByDeathDate": int,
    "cumDeathsByDeathDateRate": float,

    "newDeathsByPublishDate": int,
    "cumDeathsByPublishDate": int,
    "cumDeathsByPublishDateRate": float,

    "newDeaths28DaysByDeathDate": int,
    "newDeaths28DaysByDeathDateRate": float,
    'newDeaths28DaysByDeathDateRollingRate': float,
    'newDeaths28DaysByDeathDateRollingSum': int,
    "cumDeaths28DaysByDeathDate": int,
    "cumDeaths28DaysByDeathDateRate": float,

    "newDeaths28DaysByPublishDate": int,
    "cumDeaths28DaysByPublishDate": int,
    "cumDeaths28DaysByPublishDateRate": float,

    "newDeaths60DaysByDeathDate": int,
    "newDeaths60DaysByDeathDateRate": float,
    'newDeaths60DaysByDeathDateRollingRate': float,
    'newDeaths60DaysByDeathDateRollingSum': int,
    "cumDeaths60DaysByDeathDate": int,
    "cumDeaths60DaysByDeathDateRate": float,

    "newDeaths60DaysByPublishDate": int,
    "cumDeaths60DaysByPublishDate": int,
    "cumDeaths60DaysByPublishDateRate": float,

    'newOnsDeathsByRegistrationDate': int,
    'cumOnsDeathsByRegistrationDate': int,
    'cumOnsDeathsByRegistrationDateRate': float,

    "capacityPillarOneTwoFour": int,
    "newPillarOneTwoTestsByPublishDate": int,
    "capacityPillarOneTwo": int,
    "capacityPillarThree": int,
    "capacityPillarOne": int,
    "capacityPillarTwo": int,
    "capacityPillarFour": int,

    "cumPillarOneTwoTestsByPublishDate": int,

    "newPCRTestsByPublishDate": int,
    "cumPCRTestsByPublishDate": int,
    "plannedPCRCapacityByPublishDate": int,
    "plannedAntibodyCapacityByPublishDate": int,
    "newAntibodyTestsByPublishDate": int,
    "cumAntibodyTestsByPublishDate": int,

    "alertLevel": int,
    "transmissionRateMin": float,
    "transmissionRateMax": float,
    "transmissionRateGrowthRateMin": float,
    "transmissionRateGrowthRateMax": float,

    'newLFDTests': int,
    'cumLFDTests': int,
    'newVirusTests': int,
    'cumVirusTests': int,

    'newCasesBySpecimenDateDirection': str,
    'newCasesBySpecimenDateChange': int,
    'newCasesBySpecimenDateChangePercentage': float,
    'newCasesBySpecimenDateRollingSum': int,
    'newCasesBySpecimenDateRollingRate': float,
    'newCasesByPublishDateDirection': str,
    'newCasesByPublishDateChange': int,
    'newCasesByPublishDateChangePercentage': float,
    'newCasesByPublishDateRollingSum': int,
    'newCasesByPublishDateRollingRate': float,
    'newAdmissionsDirection': str,
    'newAdmissionsChange': int,
    'newAdmissionsChangePercentage': float,
    'newAdmissionsRollingSum': int,
    'newAdmissionsRollingRate': float,
    'newDeaths28DaysByPublishDateDirection': str,
    'newDeaths28DaysByPublishDateChange': int,
    'newDeaths28DaysByPublishDateChangePercentage': float,
    'newDeaths28DaysByPublishDateRollingSum': int,
    'newDeaths28DaysByPublishDateRollingRate': float,
    'newPCRTestsByPublishDateDirection': str,
    'newPCRTestsByPublishDateChange': int,
    'newPCRTestsByPublishDateChangePercentage': float,
    'newPCRTestsByPublishDateRollingSum': int,
    'newPCRTestsByPublishDateRollingRate': float,
    'newVirusTestsDirection': str,
    'newVirusTestsChange': int,
    'newVirusTestsChangePercentage': float,
    'newVirusTestsRollingSum': int,
    'newVirusTestsRollingRate': float,

    'newCasesByPublishDateAgeDemographics': list,
    'newCasesBySpecimenDateAgeDemographics': list,
    'newDeaths28DaysByDeathDateAgeDemographics': list,

    "uniqueCasePositivityBySpecimenDateRollingSum": float,
    "uniquePeopleTestedBySpecimenDateRollingSum": int,

    "newDailyNsoDeathsByDeathDate": int,
    "cumDailyNsoDeathsByDeathDate": int,

    "cumWeeklyNsoDeathsByRegDate": int,
    "cumWeeklyNsoDeathsByRegDateRate": float,
    "newWeeklyNsoDeathsByRegDate": int,
    "cumWeeklyNsoCareHomeDeathsByRegDate": int,
    "newWeeklyNsoCareHomeDeathsByRegDate": int,

    "newPeopleReceivingFirstDose": int,
    "cumPeopleReceivingFirstDose": int,
    "newPeopleReceivingSecondDose": int,
    "cumPeopleReceivingSecondDose": int,

    "cumPeopleVaccinatedFirstDoseByPublishDate": int,
    "cumPeopleVaccinatedSecondDoseByPublishDate": int,
    "cumPeopleVaccinatedFirstDoseByVaccinationDate": int,
    "newPeopleVaccinatedFirstDoseByPublishDate": int,
    "cumPeopleVaccinatedCompleteByPublishDate": int,
    "newPeopleVaccinatedCompleteByPublishDate": int,
    "newPeopleVaccinatedSecondDoseByPublishDate": int,
    "weeklyPeopleVaccinatedFirstDoseByVaccinationDate": int,
    "weeklyPeopleVaccinatedSecondDoseByVaccinationDate": int,
    "cumPeopleVaccinatedSecondDoseByVaccinationDate": int,

    "cumVaccinationFirstDoseUptakeByPublishDatePercentage": float,
    "cumVaccinationSecondDoseUptakeByPublishDatePercentage": float,
    "cumVaccinationCompleteCoverageByPublishDatePercentage": float,
}

# Values must be provided in lowercase characters.
# Example:
# { "areaName": ["united kingdom"] }
#
# The API will the refuse the respond to any queries
# whose filter value for a specific parameter is NOT
# in the list.
RESTRICTED_PARAMETER_VALUES: Dict[str, List[str]] = dict()

# if ENVIRONMENT != "DEVELOPMENT":
#     RESTRICTED_PARAMETER_VALUES.update({
#         "areaName": [
#             "united kingdom"
#         ],
#         "areaType": [
#             "overview",
#             "nation",
#             "nhsregion"
#         ]
#     })

if ENVIRONMENT == "DEVELOPMENT":
    DATA_TYPES: Dict[str, Callable[[str], Any]] = {
        'hash': str,
        'areaType': str,
        'date': datetime,
        'areaName': str,
        'areaNameLower': str,
        'areaCode': str,
        'changeInCumCasesBySpecimenDate': int,
        'changeInNewCasesBySpecimenDate': int,
        'cumPeopleTestedBySpecimenDate': int,
        'covidOccupiedMVBeds': int,
        'covidOccupiedNIVBeds': int,
        'covidOccupiedOSBeds': int,
        'covidOccupiedOtherBeds': int,
        'cumAdmissions': int,
        'cumAdmissionsByAge': list,
        'cumCasesByPublishDate': int,
        'cumCasesBySpecimenDate': int,
        # 'cumDeathsByDeathDate': int,
        # 'cumDeathsByPublishDate': int,
        'cumDischarges': int,
        'cumDischargesByAge': list,
        'cumNegativesBySpecimenDate': int,
        'cumPeopleTestedByPublishDate': int,
        # 'cumPillarFourPeopleTestedByPublishDate': int,  # Currently excluded.
        'cumPillarFourTestsByPublishDate': int,
        'cumPillarOnePeopleTestedByPublishDate': int,
        'cumPillarOneTestsByPublishDate': int,
        'cumPillarThreeTestsByPublishDate': int,
        'cumPillarTwoPeopleTestedByPublishDate': int,
        'cumPillarTwoTestsByPublishDate': int,
        'cumTestsByPublishDate': int,
        'femaleCases': list,
        # 'femaleDeaths': list,
        'femaleNegatives': list,
        'hospitalCases': int,
        'maleCases': list,
        # 'maleDeaths': list,
        'maleNegatives': list,
        'malePeopleTested': list,
        'femalePeopleTested': list,
        'newAdmissions': int,
        'newAdmissionsByAge': list,
        'newCasesByPublishDate': int,
        'newCasesBySpecimenDate': int,
        'newDischarges': int,
        'newNegativesBySpecimenDate': int,
        'newPeopleTestedByPublishDate': int,
        # 'newPillarFourPeopleTestedByPublishDate': int,   # Currently excluded.
        'newPillarFourTestsByPublishDate': int,
        'newPillarOnePeopleTestedByPublishDate': int,
        'newPillarOneTestsByPublishDate': int,
        'newPillarThreeTestsByPublishDate': int,
        'newPillarTwoPeopleTestedByPublishDate': int,
        'newPillarTwoTestsByPublishDate': int,
        'newTestsByPublishDate': int,
        'nonCovidOccupiedMVBeds': int,
        'nonCovidOccupiedNIVBeds': int,
        'nonCovidOccupiedOSBeds': int,
        'nonCovidOccupiedOtherBeds': int,
        'plannedCapacityByPublishDate': int,
        'plannedPillarFourCapacityByPublishDate': int,
        'plannedPillarOneCapacityByPublishDate': int,
        'plannedPillarThreeCapacityByPublishDate': int,
        'plannedPillarTwoCapacityByPublishDate': int,
        'previouslyReportedCumCasesBySpecimenDate': int,
        'previouslyReportedNewCasesBySpecimenDate': int,
        'suspectedCovidOccupiedMVBeds': int,
        'suspectedCovidOccupiedNIVBeds': int,
        'suspectedCovidOccupiedOSBeds': int,
        'suspectedCovidOccupiedOtherBeds': int,
        'totalBeds': int,
        'totalMVBeds': int,
        'totalNIVBeds': int,
        'totalOSBeds': int,
        'totalOtherBeds': int,
        'unoccupiedMVBeds': int,
        'unoccupiedNIVBeds': int,
        'unoccupiedOSBeds': int,
        'unoccupiedOtherBeds': int,
        'release': datetime,
        'newPeopleTestedBySpecimenDate': int,

        "newDeathsByDeathDate": int,
        "newDeathsByDeathDateRate": float,
        'newDeathsByDeathDateRollingRate': float,
        "cumDeathsByDeathDate": int,
        "cumDeathsByDeathDateRate": float,

        "newDeathsByPublishDate": int,
        "cumDeathsByPublishDate": int,
        "cumDeathsByPublishDateRate": float,

        "newDeaths28DaysByDeathDate": int,
        "newDeaths28DaysByDeathDateRate": float,
        'newDeaths28DaysByDeathDateRollingRate': float,
        "cumDeaths28DaysByDeathDate": int,
        "cumDeaths28DaysByDeathDateRate": float,

        "newDeaths28DaysByPublishDate": int,
        "cumDeaths28DaysByPublishDate": int,
        "cumDeaths28DaysByPublishDateRate": float,

        "newDeaths60DaysByDeathDate": int,
        "newDeaths60DaysByDeathDateRate": float,
        'newDeaths60DaysByDeathDateRollingRate': float,
        "cumDeaths60DaysByDeathDate": int,
        "cumDeaths60DaysByDeathDateRate": float,

        "femaleDeaths28Days": int,
        "femaleDeaths60Days": int,
        "maleDeaths28Days": int,
        "maleDeaths60Days": int,

        "newDeaths60DaysByPublishDate": int,
        "cumDeaths60DaysByPublishDate": int,
        "cumDeaths60DaysByPublishDateRate": float,

        'newOnsDeathsByRegistrationDate': int,
        'cumOnsDeathsByRegistrationDate': int,
        'cumOnsDeathsByRegistrationDateRate': float,

        "cumCasesBySpecimenDateRate": float,
        "cumCasesByPublishDateRate": float,
        "cumPeopleTestedByPublishDateRate": float,
        "cumAdmissionsRate": float,
        "cumDischargesRate": float,

        "capacityPillarOneTwoFour": int,
        "newPillarOneTwoTestsByPublishDate": int,
        "capacityPillarOneTwo": int,
        "capacityPillarThree": int,
        "capacityPillarOne": int,
        "capacityPillarTwo": int,
        "capacityPillarFour": int,

        "newPillarOneTwoFourTestsByPublishDate": int,
        "newCasesBySpecimenDateRate": float,

        "cumPillarOneTwoTestsByPublishDate": int,

        "newPCRTestsByPublishDate": int,
        "cumPCRTestsByPublishDate": int,
        "plannedPCRCapacityByPublishDate": int,
        "plannedAntibodyCapacityByPublishDate": int,
        "newAntibodyTestsByPublishDate": int,
        "cumAntibodyTestsByPublishDate": int,

        "newDeathsByDeathDateRollingSum": int,
        "newDeaths28DaysByDeathDateRollingSum": int,
        "newDeaths60DaysByDeathDateRollingSum": int,

        'newLFDTests': int,
        'cumLFDTests': int,
        'newVirusTests': int,
        'cumVirusTests': int,

        "alertLevel": int,
        "transmissionRateMin": float,
        "transmissionRateMax": float,
        "transmissionRateGrowthRateMin": float,
        "transmissionRateGrowthRateMax": float,

        'newCasesBySpecimenDateDirection': str,
        'newCasesBySpecimenDateChange': int,
        'newCasesBySpecimenDateChangePercentage': float,
        'newCasesBySpecimenDateRollingSum': int,
        'newCasesBySpecimenDateRollingRate': float,
        'newCasesByPublishDateDirection': str,
        'newCasesByPublishDateChange': int,
        'newCasesByPublishDateChangePercentage': float,
        'newCasesByPublishDateRollingSum': int,
        'newCasesByPublishDateRollingRate': float,
        'newAdmissionsDirection': str,
        'newAdmissionsChange': int,
        'newAdmissionsChangePercentage': float,
        'newAdmissionsRollingSum': int,
        'newAdmissionsRollingRate': float,
        'newDeaths28DaysByPublishDateDirection': str,
        'newDeaths28DaysByPublishDateChange': int,
        'newDeaths28DaysByPublishDateChangePercentage': float,
        'newDeaths28DaysByPublishDateRollingSum': int,
        'newDeaths28DaysByPublishDateRollingRate': float,
        'newPCRTestsByPublishDateDirection': str,
        'newPCRTestsByPublishDateChange': int,
        'newPCRTestsByPublishDateChangePercentage': float,
        'newPCRTestsByPublishDateRollingSum': int,
        'newPCRTestsByPublishDateRollingRate': float,
        'newVirusTestsDirection': str,
        'newVirusTestsChange': int,
        'newVirusTestsChangePercentage': float,
        'newVirusTestsRollingSum': int,
        'newVirusTestsRollingRate': float,

        "newOnsCareHomeDeathsByRegistrationDate": int,
        "cumOnsCareHomeDeathsByRegistrationDate": int,

        'newCasesByPublishDateAgeDemographics': list,
        'newCasesBySpecimenDateAgeDemographics': list,
        'newDeaths28DaysByDeathDateAgeDemographics': list,

        "uniqueCasePositivityBySpecimenDateRollingSum": float,
        "uniquePeopleTestedBySpecimenDateRollingSum": int,

        "newPeopleReceivingFirstDose": int,
        "cumPeopleReceivingFirstDose": int,
        "newPeopleReceivingSecondDose": int,
        "cumPeopleReceivingSecondDose": int,

        "cumWeeklyNsoDeathsByRegDate": int,
        "cumWeeklyNsoDeathsByRegDateRate": float,
        "newWeeklyNsoDeathsByRegDate": int,
        "cumWeeklyNsoCareHomeDeathsByRegDate": int,
        "newWeeklyNsoCareHomeDeathsByRegDate": int,

        "newDailyNsoDeathsByDeathDate": int,
        "cumDailyNsoDeathsByDeathDate": int,

        "cumPeopleVaccinatedFirstDoseByPublishDate": int,
        "cumPeopleVaccinatedSecondDoseByPublishDate": int,
        "cumPeopleVaccinatedFirstDoseByVaccinationDate": int,
        "newPeopleVaccinatedFirstDoseByPublishDate": int,
        "cumPeopleVaccinatedCompleteByPublishDate": int,
        "newPeopleVaccinatedCompleteByPublishDate": int,
        "newPeopleVaccinatedSecondDoseByPublishDate": int,
        "weeklyPeopleVaccinatedFirstDoseByVaccinationDate": int,
        "weeklyPeopleVaccinatedSecondDoseByVaccinationDate": int,
        "cumPeopleVaccinatedSecondDoseByVaccinationDate": int,

        'newCasesPCROnlyBySpecimenDateRollingSum': int,
        'newCasesLFDOnlyBySpecimenDateRollingRate': float,
        'newCasesLFDOnlyBySpecimenDate': int,
        'newCasesLFDConfirmedPCRBySpecimenDate': int,
        'newCasesLFDConfirmedPCRBySpecimenDateRollingRate': float,
        'cumCasesPCROnlyBySpecimenDate': int,
        'newCasesPCROnlyBySpecimenDateRollingRate': float,
        'newCasesLFDOnlyBySpecimenDateRollingSum': int,
        'cumCasesLFDConfirmedPCRBySpecimenDate': int,
        'cumCasesLFDOnlyBySpecimenDate': int,
        'newCasesPCROnlyBySpecimenDate': int,
        'newCasesLFDConfirmedPCRBySpecimenDateRollingSum': int,

        "cumVaccinationFirstDoseUptakeByPublishDatePercentage": float,
        "cumVaccinationSecondDoseUptakeByPublishDatePercentage": float,
        "cumVaccinationCompleteCoverageByPublishDatePercentage": float,
    }
