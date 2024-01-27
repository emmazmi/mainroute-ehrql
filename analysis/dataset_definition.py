from ehrql import Dataset, years, days, minimum_of, maximum_of
from ehrql.tables.core import patients, clinical_events
from ehrql.tables.tpp import practice_registrations, ons_deaths

import codelists

def make_dataset_lowerGI(index_date, end_date):
    
    dataset = Dataset()

    reg_date = practice_registrations.where(practice_registrations.start_date.is_on_or_between(index_date, end_date)
                                                    ).sort_by(
                                                        practice_registrations.start_date
                                                    ).first_for_patient().start_date
    
    age_16_date = patients.date_of_birth + years(16)

    dataset.entry_date = maximum_of(reg_date, age_16_date, "2018-03-23")

    def event_date(codelist):
        return clinical_events.where(clinical_events.snomedct_code.is_in(codelist)
            ).where(
                clinical_events.date.is_on_or_between(index_date, end_date)
            ).sort_by(
                clinical_events.date
            ).first_for_patient().date
    
    def prev_event(codelist, symp_date):
        return clinical_events.where(clinical_events.snomedct_code.is_in(codelist)
            ).where(
                clinical_events.date.is_on_or_between(symp_date - days (42), symp_date)
            ).exists_for_patient()

    dataset.ida_date = event_date(codelists.ida_codes)
    dataset.cibh_date = event_date(codelists.cibh_codes)
    dataset.prbleed_date = event_date(codelists.prbleeding_codes)
    dataset.wl_date = event_date(codelists.wl_codes)
    dataset.abdomass_date = event_date(codelists.abdomass_codes)
    dataset.abdopain_date = event_date(codelists.abdopain_codes)
    dataset.anaemia_date = event_date(codelists.anaemia_codes)

    dataset.fit_date = event_date(codelists.fit_codes)
    dataset.colorectal_ca_diagnosis_date = event_date(codelists.colorectal_diagnosis_codes_snomed)

    dataset.ida_prev = prev_event(codelists.ida_codes, dataset.ida_date)
    dataset.cibh_prev = prev_event(codelists.cibh_codes, dataset.cibh_date)
    dataset.prbleed_prev = prev_event(codelists.prbleeding_codes, dataset.prbleed_date)
    dataset.wl_prev = prev_event(codelists.wl_codes, dataset.wl_date)
    dataset.abdomass_prev = prev_event(codelists.abdomass_codes, dataset.abdomass_date)
    dataset.abdopain_prev = prev_event(codelists.abdopain_codes, dataset.abdopain_date)
    dataset.anaemia_prev = prev_event(codelists.anaemia_codes, dataset.anaemia_date)
    dataset.fit_prev = prev_event(codelists.fit_codes, dataset.fit_date)

    dataset.ida_symp = dataset.ida_date.is_not_null() & ~dataset.ida_prev
    dataset.cibh_symp = dataset.cibh_date.is_not_null() & ~dataset.cibh_prev
    dataset.abdomass_symp = dataset.abdomass_date.is_not_null() & ~dataset.abdomass_prev
    dataset.prbleed_symp_50 = dataset.prbleed_date.is_not_null() & (patients.age_on(dataset.prbleed_date) >= 50) & ~dataset.prbleed_prev
    dataset.wl_symp_50 = dataset.wl_date.is_not_null() & (patients.age_on(dataset.wl_date) >= 50) & ~dataset.wl_prev
    dataset.abdopain_symp_50 = dataset.abdopain_date.is_not_null() & (patients.age_on(dataset.abdopain_date) >= 50) & ~dataset.abdopain_prev
    dataset.anaemia_symp = dataset.anaemia_date.is_not_null() & (patients.age_on(dataset.anaemia_date) >= 60) & ~dataset.anaemia_prev
    dataset.wl_abdopain_symp_40 = dataset.wl_date.is_not_null() & dataset.abdopain_date.is_not_null() & ((patients.age_on(dataset.wl_date) >= 40) | (patients.age_on(dataset.abdopain_date) >= 40)) & ~dataset.wl_prev & ~dataset.abdopain_prev
    dataset.prbleed_abdopain_symp = dataset.prbleed_date.is_not_null() & dataset.abdopain_date.is_not_null() & (patients.age_on(dataset.prbleed_date) < 50) & ~dataset.prbleed_prev & ~dataset.abdopain_prev
    dataset.prbleed_wl_symp = dataset.prbleed_date.is_not_null() & dataset.wl_date.is_not_null() & (patients.age_on(dataset.prbleed_date) < 50) & ~dataset.prbleed_prev & ~dataset.wl_prev

    dataset.fit_test = dataset.fit_date.is_not_null() & ~dataset.fit_prev
    dataset.colorectal_ca_diagnosis = dataset.colorectal_ca_diagnosis_date.is_not_null()

    death_date = ons_deaths.date

    age_110_date = patients.date_of_birth + years(110)

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
    
    dataset.exit_date = minimum_of(death_date, age_110_date, dereg_date, colorectal_ca_diag_date)

    dataset.death_date = death_date

    return dataset

