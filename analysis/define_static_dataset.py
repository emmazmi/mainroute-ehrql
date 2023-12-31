from ehrql import case, when
from ehrql.tables.core import patients, clinical_events
from ehrql.tables.tpp import ( 
    addresses,
    practice_registrations)

import codelists

from dataset_definition import make_dataset_colorectal

dataset = make_dataset_colorectal(index_date="2018-03-23", end_date="2023-10-22")

was_adult = (patients.age_on("2023-10-22") >= 16) & (
    patients.age_on("2018-03-23") <= 110
)

was_alive = (
    patients.date_of_death.is_after("2018-03-23")
    | patients.date_of_death.is_null()
)

was_registered = practice_registrations.where(
        (practice_registrations.start_date.is_on_or_before("2018-03-23") & (practice_registrations.end_date.is_after("2018-03-23") | practice_registrations.end_date.is_null()))
         | (practice_registrations.start_date.is_after("2018-03-23") & practice_registrations.start_date.is_on_or_before("2023-10-22"))
).exists_for_patient()

no_prev_colorectal_ca = clinical_events.except_where(
            clinical_events.snomedct_code.is_in(codelists.colorectal_diagnosis_codes_snomed)
        ).where(
            clinical_events.date.is_on_or_before("2018-03-23")
    ).exists_for_patient()
    
dataset.define_population(
    was_adult
    & was_alive
    & was_registered
    & no_prev_colorectal_ca
)

age = patients.age_on(dataset.entry_date)
dataset.age_group = case(
        when(age < 30).then("16-29"),
        when(age < 40).then("30-39"),
        when(age < 50).then("40-49"),
        when(age < 60).then("50-59"),
        when(age < 70).then("60-69"),
        when(age < 80).then("70-79"),
        when(age < 90).then("80-89"),
        when(age >= 90).then("90+"),
        otherwise="missing",
)

dataset.sex = patients.sex

imd = addresses.for_patient_on(dataset.entry_date).imd_rounded
dataset.imd10 = case(
        when((imd >= 0) & (imd < int(32844 * 1 / 10))).then("1 (most deprived)"),
        when(imd < int(32844 * 2 / 10)).then("2"),
        when(imd < int(32844 * 3 / 10)).then("3"),
        when(imd < int(32844 * 4 / 10)).then("4"),
        when(imd < int(32844 * 5 / 10)).then("5"),
        when(imd < int(32844 * 6 / 10)).then("6"),
        when(imd < int(32844 * 7 / 10)).then("7"),
        when(imd < int(32844 * 8 / 10)).then("8"),
        when(imd < int(32844 * 9 / 10)).then("9"),
        when(imd >= int(32844 * 9 / 10)).then("10 (least deprived)"),
        otherwise="unknown"
)

ethnicity16 = clinical_events.where(clinical_events.snomedct_code.is_in(codelists.ethnicity_codes_16)
    ).where(
        clinical_events.date.is_on_or_before(dataset.entry_date)
    ).sort_by(
        clinical_events.date
    ).last_for_patient().snomedct_code.to_category(codelists.ethnicity_codes_16)

dataset.ethnicity16 = case(
    when(ethnicity16 == "1").then("White - British"),
    when(ethnicity16 == "2").then("White - Irish"),
    when(ethnicity16 == "3").then("White - Other"),
    when(ethnicity16 == "4").then("Mixed - White/Black Caribbean"),
    when(ethnicity16 == "5").then("Mixed - White/Black African"),
    when(ethnicity16 == "6").then("Mixed - White/Asian"),
    when(ethnicity16 == "7").then("Mixed - Other"),
    when(ethnicity16 == "8").then("Asian or Asian British - Indian"),
    when(ethnicity16 == "9").then("Asian or Asian British - Pakistani"),
    when(ethnicity16 == "10").then("Asian or Asian British - Bangladeshi"),
    when(ethnicity16 == "11").then("Asian or Asian British - Other"),
    when(ethnicity16 == "12").then("Black - Caribbean"),    
    when(ethnicity16 == "13").then("Black - African"),
    when(ethnicity16 == "14").then("Black - Other"),
    when(ethnicity16 == "15").then("Other - Chinese"),
    when(ethnicity16 == "16").then("Other - Other"),
    otherwise="Unknown"
)

ethnicity6 = clinical_events.where(
        clinical_events.snomedct_code.is_in(codelists.ethnicity_codes_6)
    ).where(
        clinical_events.date.is_on_or_before(dataset.entry_date)
    ).sort_by(
        clinical_events.date
    ).last_for_patient().snomedct_code.to_category(codelists.ethnicity_codes_6)

dataset.ethnicity6 = case(
    when(ethnicity6 == "1").then("White"),
    when(ethnicity6 == "2").then("Mixed"),
    when(ethnicity6 == "3").then("South Asian"),
    when(ethnicity6 == "4").then("Black"),
    when(ethnicity6 == "5").then("Other"),
    when(ethnicity6 == "6").then("Not stated"),
    otherwise="Unknown"
)

dataset.region = practice_registrations.for_patient_on("2022-04-01").practice_nuts1_region_name