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
        practice_registrations.for_patient_on("2018-03-23")
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