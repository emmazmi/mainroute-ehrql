from ehrql import case, when, months, INTERVAL, Measures, minimum_of, maximum_of
from ehrql.tables.tpp import (
    patients, 
    addresses,
    practice_registrations,
    clinical_events)

import codelists

from dataset_definition import make_dataset_lowerGI

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--start-date", type=str)
parser.add_argument("--intervals", type=int)

args = parser.parse_args()

start_date = args.start_date
intervals = args.intervals

##########

index_date = INTERVAL.start_date

dataset = make_dataset_lowerGI(index_date=index_date, end_date=INTERVAL.end_date)

dataset.elig_cohort = dataset.entry_date.is_on_or_before(INTERVAL.end_date) & dataset.exit_date.is_after(index_date)

period_entry = maximum_of(index_date, dataset.entry_date)
period_exit = minimum_of(INTERVAL.end_date, dataset.exit_date)

follow_up_years = (period_exit - period_entry).years

elig_follow_up_years = case(
        when(dataset.elig_cohort).then(follow_up_years)
)

##########

## Define demographic variables

age = patients.age_on(dataset.entry_date)
age_group = case(
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

sex = patients.sex

imd = addresses.for_patient_on(dataset.entry_date).imd_rounded
imd5 = case(
        when((imd >=0) & (imd < int(32844 * 1 / 5))).then("1 (most deprived)"),
        when(imd < int(32844 * 2 / 5)).then("2"),
        when(imd < int(32844 * 3 / 5)).then("3"),
        when(imd < int(32844 * 4 / 5)).then("4"),
        when(imd < int(32844 * 5 / 5)).then("5 (least deprived)"),
        otherwise="unknown"
)

ethnicity6 = clinical_events.where(
        clinical_events.snomedct_code.is_in(codelists.ethnicity_codes_6)
    ).where(
        clinical_events.date.is_on_or_before(dataset.entry_date)
    ).sort_by(
        clinical_events.date
    ).last_for_patient().snomedct_code.to_category(codelists.ethnicity_codes_6)

ethnicity6 = case(
    when(ethnicity6 == "1").then("White"),
    when(ethnicity6 == "2").then("Mixed"),
    when(ethnicity6 == "3").then("South Asian"),
    when(ethnicity6 == "4").then("Black"),
    when(ethnicity6 == "5").then("Other"),
    when(ethnicity6 == "6").then("Not stated"),
    otherwise="Unknown"
)

region = practice_registrations.for_patient_on(dataset.entry_date).practice_nuts1_region_name

#########################

measures = Measures()
measures.configure_disclosure_control(enabled=False)

measures.define_defaults(intervals=months(intervals).starting_on(start_date))

measures.define_measure(
    name="fit_test_rate", 
    numerator=dataset.fit_test_all & dataset.elig_cohort,
    denominator=elig_follow_up_years,
    group_by={"imd": imd5}
    )

measures.define_measure(
    name="ida_symp_rate", 
    numerator=dataset.ida_symp & dataset.elig_cohort,
    denominator=elig_follow_up_years,
    group_by={"imd": imd5}
    )

measures.define_measure(
    name="cibh_symp_rate", 
    numerator=dataset.cibh_symp & dataset.elig_cohort,
    denominator=elig_follow_up_years,
    group_by={"imd": imd5}
    )

measures.define_measure(
    name="abdomass_symp_rate", 
    numerator=dataset.abdomass_symp & dataset.elig_cohort,
    denominator=elig_follow_up_years,
    group_by={"imd": imd5}
    )

measures.define_measure(
    name="prbleed_symp_50_rate", 
    numerator=dataset.prbleed_symp_50 & dataset.elig_cohort,
    denominator=elig_follow_up_years,
    group_by={"imd": imd5}
    )

measures.define_measure(
    name="wl_symp_50_rate", 
    numerator=dataset.wl_symp_50 & dataset.elig_cohort,
    denominator=elig_follow_up_years,
    group_by={"imd": imd5}
    )

measures.define_measure(
    name="abdopain_symp_50_rate", 
    numerator=dataset.abdopain_symp_50 & dataset.elig_cohort,
    denominator=elig_follow_up_years,
    group_by={"imd": imd5}
    )

measures.define_measure(
    name="anaemia_symp_60_rate", 
    numerator=dataset.anaemia_symp_60 & dataset.elig_cohort,
    denominator=elig_follow_up_years,
    group_by={"imd": imd5}
    )