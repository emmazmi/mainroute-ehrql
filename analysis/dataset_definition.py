from ehrql import Dataset, minimum_of
from ehrql.tables.core import patients, clinical_events
from ehrql.tables.tpp import practice_registrations

import codelists

def make_dataset_colorectal(index_date, end_date):
    
    dataset = Dataset()

    was_adult = (patients.age_on(index_date) >= 16) & (
    patients.age_on(index_date) <= 110
    )

    was_alive = (
    patients.date_of_death.is_after(index_date)
    | patients.date_of_death.is_null()
    )

    was_registered = practice_registrations.where(
        practice_registrations.for_patient_on(index_date)
        | (practice_registrations.start_date.is_after(index_date) & practice_registrations.start_date.is_on_or_before(end_date))
    ).exists_for_patient()

    prev_colorectal_ca = clinical_events.where(
            clinical_events.snomedct_code.is_in(codelists.colorectal_diagnosis_codes_snomed)
        ).where(
            clinical_events.date.is_on_or_before(index_date)
        ).exists_for_patient()
    
    dataset.reg_date = practice_registrations.where(practice_registrations.start_date.is_on_or_between(index_date, end_date)
                                                    ).sort_by(
                                                        practice_registrations.start_date
                                                    ).first_for_patient().start_date
    
    def has_symptom(codelist):
        return clinical_events.where(clinical_events.snomedct_code.is_in(codelist)
            ).where(
                clinical_events.date.is_on_or_between(index_date, end_date)
            ).exists_for_patient()
    
    dataset.lowerGI_symp_any = has_symptom(codelists.colorectal_symptom_codes)

    dataset.ida_symp = has_symptom(codelists.ida_codes)
    dataset.cibh_symp = has_symptom(codelists.cibh_codes)
    dataset.prbleed_symp = has_symptom(codelists.prbleeding_codes)
    dataset.wl_symp = has_symptom(codelists.wl_codes)
    dataset.abdomass_symp = has_symptom(codelists.abdomass_codes)
    dataset.abdopain_symp = has_symptom(codelists.abdopain_codes)
    dataset.anaemia_symp = has_symptom(codelists.anaemia_codes)

    death_date = patients.where(patients.date_of_death.is_on_or_between(index_date, end_date)
                                ).sort_by(
                                    patients.date_of_death
                                ).first_for_patient().date_of_death

    dereg_date = practice_registrations.where(practice_registrations.end_date.is_on_or_between(index_date, end_date)
                                              ).sort_by(
                                                  practice_registrations.end_date
                                              ).first_for_patient().end_date

    colorectal_ca_diag_date = clinical_events.where(clinical_events.snomedct_code.is_in(codelists.colorectal_diagnosis_codes_snomed)
                                                        ).where(
                                                            clinical_events.date.is_on_or_between(index_date, end_date)
                                                        ).sort_by(
                                                            clinical_events.date
                                                        ).first_for_patient().date
    
    dataset.exit_date = minimum_of(death_date, dereg_date, colorectal_ca_diag_date)

    return dataset

