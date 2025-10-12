import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Define constants
NUM_ROWS = 10000
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 12, 31)
OUTPUT_PATH = r"YOUR PATH" #YOUR SYSTEM PATH

print("Starting data generation...")

# ============================================================================
# 1. DimPatient
# ============================================================================
print("Generating DimPatient...")

genders = ['Male', 'Female', 'Non-Binary', 'Prefer not to say']
races = ['White', 'Black/African American', 'Hispanic/Latino', 'Asian', 
         'Native American', 'Pacific Islander', 'Two or More Races', 'Other']
regions = ['North', 'South', 'East', 'West', 'Central']
insurance_types = ['Medicare', 'Medicaid', 'Private', 'Self-Pay', 'Military']

dim_patient = pd.DataFrame({
    'PatientID': [f'P{str(i).zfill(6)}' for i in range(1, NUM_ROWS + 1)],
    'Age': np.random.randint(18, 90, NUM_ROWS),
    'Gender': np.random.choice(genders, NUM_ROWS, p=[0.48, 0.48, 0.02, 0.02]),
    'Race': np.random.choice(races, NUM_ROWS, p=[0.40, 0.20, 0.18, 0.10, 0.03, 0.02, 0.05, 0.02]),
    'Region': np.random.choice(regions, NUM_ROWS),
    'InsuranceType': np.random.choice(insurance_types, NUM_ROWS, p=[0.25, 0.15, 0.45, 0.10, 0.05]),
    'PortalRegistered': np.random.choice([True, False], NUM_ROWS, p=[0.65, 0.35])
})

dim_patient.to_csv(f'{OUTPUT_PATH}\\DimPatient.csv', index=False)
print(f"✓ DimPatient saved ({len(dim_patient)} rows)")

# ============================================================================
# 2. DimProvider
# ============================================================================
print("Generating DimProvider...")

specialties = ['Primary Care', 'Cardiology', 'Orthopedics', 'Dermatology', 
               'Neurology', 'Pediatrics', 'OB/GYN', 'Psychiatry', 'Oncology',
               'Emergency Medicine', 'Radiology', 'Surgery']
facilities = ['Main Hospital', 'North Clinic', 'South Clinic', 'East Medical Center',
              'West Urgent Care', 'Central Health Plaza', 'Downtown Facility']

dim_provider = pd.DataFrame({
    'ProviderID': [f'PR{str(i).zfill(4)}' for i in range(1, 501)],
    'Specialty': np.random.choice(specialties, 500),
    'Region': np.random.choice(regions, 500),
    'Facility': np.random.choice(facilities, 500)
})

dim_provider.to_csv(f'{OUTPUT_PATH}\\DimProvider.csv', index=False)
print(f"✓ DimProvider saved ({len(dim_provider)} rows)")

# ============================================================================
# 3. DimDate
# ============================================================================
print("Generating DimDate...")

date_range = pd.date_range(start=START_DATE, end=END_DATE, freq='D')
dim_date = pd.DataFrame({
    'Date': date_range,
    'Month': date_range.month,
    'Quarter': date_range.quarter,
    'Year': date_range.year
})

dim_date.to_csv(f'{OUTPUT_PATH}\\DimDate.csv', index=False)
print(f"✓ DimDate saved ({len(dim_date)} rows)")

# ============================================================================
# 4. FactAppointments
# ============================================================================
print("Generating FactAppointments...")

statuses = ['Completed', 'Cancelled', 'No-Show', 'Scheduled']
cancel_reasons = ['Patient Request', 'Provider Unavailable', 'Insurance Issue', 
                  'Transportation', 'Feeling Better', 'Cost Concerns', 'Other', None]

fact_appointments = pd.DataFrame({
    'AppointmentID': [f'A{str(i).zfill(7)}' for i in range(1, NUM_ROWS + 1)],
    'PatientID': np.random.choice(dim_patient['PatientID'], NUM_ROWS),
    'ProviderID': np.random.choice(dim_provider['ProviderID'], NUM_ROWS)
})

# Generate dates
date_requested = [START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days)) 
                  for _ in range(NUM_ROWS)]

# Generate wait times with realistic distribution (most within 1-30 days)
wait_time_days = np.random.choice(
    [1, 3, 5, 7, 10, 14, 21, 30, 45, 60],
    NUM_ROWS,
    p=[0.15, 0.20, 0.20, 0.15, 0.12, 0.08, 0.05, 0.03, 0.01, 0.01]
)
date_scheduled = [dr + timedelta(days=int(wt)) for dr, wt in zip(date_requested, wait_time_days)]

fact_appointments['DateRequested'] = date_requested
fact_appointments['DateScheduled'] = date_scheduled
fact_appointments['WaitTimeDays'] = wait_time_days
fact_appointments['Status'] = np.random.choice(statuses, NUM_ROWS, p=[0.75, 0.12, 0.08, 0.05])

# DateCompleted only for completed appointments
fact_appointments['DateCompleted'] = fact_appointments.apply(
    lambda row: row['DateScheduled'] if row['Status'] == 'Completed' else None, axis=1
)

# CancelReason only for cancelled appointments
fact_appointments['CancelReason'] = fact_appointments.apply(
    lambda row: random.choice(cancel_reasons[:-1]) if row['Status'] == 'Cancelled' else None, axis=1
)

fact_appointments.to_csv(f'{OUTPUT_PATH}\\FactAppointments.csv', index=False)
print(f"✓ FactAppointments saved ({len(fact_appointments)} rows)")

# ============================================================================
# 5. FactBilling
# ============================================================================
print("Generating FactBilling...")

fact_billing = pd.DataFrame({
    'BillID': [f'B{str(i).zfill(7)}' for i in range(1, NUM_ROWS + 1)],
    'PatientID': np.random.choice(dim_patient['PatientID'], NUM_ROWS),
    'DateOfService': [START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days)) 
                      for _ in range(NUM_ROWS)]
})

# Generate charges based on realistic distributions
total_charges = np.random.choice(
    [100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000],
    NUM_ROWS,
    p=[0.15, 0.20, 0.25, 0.20, 0.10, 0.05, 0.03, 0.015, 0.005]
)

fact_billing['TotalCharge'] = total_charges
fact_billing['Denied'] = np.random.choice([True, False], NUM_ROWS, p=[0.08, 0.92])

# Calculate insurance payment (70-95% of total for non-denied)
insurance_coverage = np.random.uniform(0.70, 0.95, NUM_ROWS)
fact_billing['InsurancePaid'] = fact_billing.apply(
    lambda row: 0 if row['Denied'] else row['TotalCharge'] * insurance_coverage[row.name], axis=1
)

fact_billing['PatientOOP'] = fact_billing['TotalCharge'] - fact_billing['InsurancePaid']
fact_billing['Appealed'] = fact_billing['Denied'] & (np.random.random(NUM_ROWS) < 0.40)

# Round to 2 decimals
fact_billing['TotalCharge'] = fact_billing['TotalCharge'].round(2)
fact_billing['InsurancePaid'] = fact_billing['InsurancePaid'].round(2)
fact_billing['PatientOOP'] = fact_billing['PatientOOP'].round(2)

fact_billing.to_csv(f'{OUTPUT_PATH}\\FactBilling.csv', index=False)
print(f"✓ FactBilling saved ({len(fact_billing)} rows)")

# ============================================================================
# 6. FactReferrals
# ============================================================================
print("Generating FactReferrals...")

referral_statuses = ['Complete', 'Incomplete', 'Pending', 'Cancelled']

fact_referrals = pd.DataFrame({
    'ReferralID': [f'R{str(i).zfill(7)}' for i in range(1, NUM_ROWS + 1)],
    'PatientID': np.random.choice(dim_patient['PatientID'], NUM_ROWS),
    'FromProviderID': np.random.choice(dim_provider['ProviderID'], NUM_ROWS),
    'ToProviderID': np.random.choice(dim_provider['ProviderID'], NUM_ROWS)
})

referral_dates = [START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days)) 
                  for _ in range(NUM_ROWS)]
fact_referrals['ReferralDate'] = referral_dates
fact_referrals['Status'] = np.random.choice(referral_statuses, NUM_ROWS, p=[0.65, 0.15, 0.12, 0.08])

# AppointmentDate only for complete/pending referrals
fact_referrals['AppointmentDate'] = fact_referrals.apply(
    lambda row: row['ReferralDate'] + timedelta(days=random.randint(7, 45)) 
    if row['Status'] in ['Complete', 'Pending'] else None, axis=1
)

fact_referrals.to_csv(f'{OUTPUT_PATH}\\FactReferrals.csv', index=False)
print(f"✓ FactReferrals saved ({len(fact_referrals)} rows)")

# ============================================================================
# 7. FactReadmissions
# ============================================================================
print("Generating FactReadmissions...")

# Generate fewer readmissions (about 12% of patients)
num_readmissions = int(NUM_ROWS * 0.12)

fact_readmissions = pd.DataFrame({
    'ReadmissionID': [f'RA{str(i).zfill(6)}' for i in range(1, num_readmissions + 1)],
    'PatientID': np.random.choice(dim_patient['PatientID'], num_readmissions)
})

discharge_dates = [START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days - 90)) 
                   for _ in range(num_readmissions)]
fact_readmissions['DischargeDate'] = discharge_dates

# Days between weighted toward 30-day readmissions
days_between = np.random.choice(range(1, 181), num_readmissions,
                                p=[0.45/30]*30 + [0.30/60]*60 + [0.25/90]*90)
fact_readmissions['DaysBetween'] = days_between
fact_readmissions['ReadmissionDate'] = [dd + timedelta(days=int(db)) 
                                         for dd, db in zip(discharge_dates, days_between)]

fact_readmissions.to_csv(f'{OUTPUT_PATH}\\FactReadmissions.csv', index=False)
print(f"✓ FactReadmissions saved ({len(fact_readmissions)} rows)")

# ============================================================================
# 8. FactSurveys
# ============================================================================
print("Generating FactSurveys...")

fact_surveys = pd.DataFrame({
    'SurveyID': [f'S{str(i).zfill(7)}' for i in range(1, NUM_ROWS + 1)],
    'PatientID': np.random.choice(dim_patient['PatientID'], NUM_ROWS),
    'Date': [START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days)) 
             for _ in range(NUM_ROWS)]
})

# Survey scores (1-10 scale, weighted toward positive)
fact_surveys['HCAHPSScore'] = np.random.choice(range(1, 11), NUM_ROWS,
                                                p=[0.02, 0.02, 0.03, 0.05, 0.08, 0.12, 0.18, 0.20, 0.18, 0.12])
fact_surveys['TrustScore'] = np.random.choice(range(1, 11), NUM_ROWS,
                                               p=[0.03, 0.03, 0.04, 0.06, 0.10, 0.14, 0.18, 0.18, 0.14, 0.10])
fact_surveys['CommunicationScore'] = np.random.choice(range(1, 11), NUM_ROWS,
                                                       p=[0.02, 0.03, 0.04, 0.07, 0.10, 0.15, 0.19, 0.18, 0.14, 0.08])
fact_surveys['WaitTimeRating'] = np.random.choice(range(1, 11), NUM_ROWS,
                                                   p=[0.05, 0.06, 0.08, 0.10, 0.12, 0.15, 0.16, 0.14, 0.10, 0.04])
fact_surveys['CostClarityScore'] = np.random.choice(range(1, 11), NUM_ROWS,
                                                     p=[0.08, 0.08, 0.10, 0.12, 0.14, 0.15, 0.14, 0.10, 0.06, 0.03])

fact_surveys.to_csv(f'{OUTPUT_PATH}\\FactSurveys.csv', index=False)
print(f"✓ FactSurveys saved ({len(fact_surveys)} rows)")

# ============================================================================
# 9. FactPortalUsage
# ============================================================================
print("Generating FactPortalUsage...")

features = ['View Records', 'Schedule Appointment', 'Message Provider', 
            'View Bills', 'Request Refill', 'Update Info', 'View Lab Results']

# Only registered patients use portal
portal_patients = dim_patient[dim_patient['PortalRegistered'] == True]['PatientID'].tolist()
num_portal_logs = NUM_ROWS

fact_portal_usage = pd.DataFrame({
    'LogID': [f'L{str(i).zfill(7)}' for i in range(1, num_portal_logs + 1)],
    'PatientID': np.random.choice(portal_patients, num_portal_logs),
    'Date': [START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days)) 
             for _ in range(num_portal_logs)],
    'LoginCount': np.random.choice(range(1, 11), num_portal_logs, p=[0.40, 0.25, 0.15, 0.08, 0.05, 0.03, 0.02, 0.01, 0.005, 0.005]),
    'FeatureUsed': np.random.choice(features, num_portal_logs, p=[0.25, 0.20, 0.18, 0.15, 0.10, 0.07, 0.05])
})

fact_portal_usage.to_csv(f'{OUTPUT_PATH}\\FactPortalUsage.csv', index=False)
print(f"✓ FactPortalUsage saved ({len(fact_portal_usage)} rows)")

# ============================================================================
# 10. FactComplaints
# ============================================================================
print("Generating FactComplaints...")

complaint_categories = ['Billing Confusion', 'Long Wait Time', 'Poor Communication',
                        'Staff Attitude', 'Cultural Insensitivity', 'Appointment Scheduling',
                        'Medical Care Quality', 'Facility Cleanliness', 'Other']

num_complaints = int(NUM_ROWS * 0.08)  # About 8% of interactions have complaints

fact_complaints = pd.DataFrame({
    'ComplaintID': [f'C{str(i).zfill(6)}' for i in range(1, num_complaints + 1)],
    'PatientID': np.random.choice(dim_patient['PatientID'], num_complaints),
    'Date': [START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days)) 
             for _ in range(num_complaints)],
    'Category': np.random.choice(complaint_categories, num_complaints,
                                 p=[0.25, 0.20, 0.15, 0.12, 0.03, 0.10, 0.08, 0.04, 0.03]),
    'Resolved': np.random.choice([True, False], num_complaints, p=[0.85, 0.15])
})

fact_complaints.to_csv(f'{OUTPUT_PATH}\\FactComplaints.csv', index=False)
print(f"✓ FactComplaints saved ({len(fact_complaints)} rows)")

# ============================================================================
# 11. FactTelehealth
# ============================================================================
print("Generating FactTelehealth...")

dropout_reasons = ['Tech Issues', 'Connection Problem', 'Patient No-Show', 
                   'Provider Issue', 'Scheduling Error', None]

num_telehealth = int(NUM_ROWS * 0.30)  # 30% of appointments are telehealth

fact_telehealth = pd.DataFrame({
    'SessionID': [f'T{str(i).zfill(7)}' for i in range(1, num_telehealth + 1)],
    'PatientID': np.random.choice(dim_patient['PatientID'], num_telehealth),
    'Date': [START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days)) 
             for _ in range(num_telehealth)],
    'Completed': np.random.choice([True, False], num_telehealth, p=[0.88, 0.12])
})

fact_telehealth['DropoffReason'] = fact_telehealth.apply(
    lambda row: random.choice(dropout_reasons[:-1]) if not row['Completed'] else None, axis=1
)

fact_telehealth['TechIssue'] = fact_telehealth['DropoffReason'].isin(['Tech Issues', 'Connection Problem'])

fact_telehealth.to_csv(f'{OUTPUT_PATH}\\FactTelehealth.csv', index=False)
print(f"✓ FactTelehealth saved ({len(fact_telehealth)} rows)")

# ============================================================================
# 12. FactInterpreter
# ============================================================================
print("Generating FactInterpreter...")

languages = ['Spanish', 'Mandarin', 'Vietnamese', 'Tagalog', 'Korean', 
             'Russian', 'Arabic', 'French', 'Portuguese', 'ASL']

num_interpreter = int(NUM_ROWS * 0.12)  # 12% of appointments need interpreters

fact_interpreter = pd.DataFrame({
    'ServiceID': [f'I{str(i).zfill(6)}' for i in range(1, num_interpreter + 1)],
    'PatientID': np.random.choice(dim_patient['PatientID'], num_interpreter),
    'ProviderID': np.random.choice(dim_provider['ProviderID'], num_interpreter),
    'Date': [START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days)) 
             for _ in range(num_interpreter)],
    'Language': np.random.choice(languages, num_interpreter,
                                 p=[0.45, 0.12, 0.10, 0.08, 0.06, 0.05, 0.05, 0.04, 0.03, 0.02])
})

fact_interpreter.to_csv(f'{OUTPUT_PATH}\\FactInterpreter.csv', index=False)
print(f"✓ FactInterpreter saved ({len(fact_interpreter)} rows)")

# ============================================================================
# Summary Report
# ============================================================================
print("\n" + "="*60)
print("DATA GENERATION COMPLETE!")
print("="*60)
print(f"\nAll files saved to: {OUTPUT_PATH}\n")
print("Summary of generated files:")
print(f"1. DimPatient.csv: {len(dim_patient):,} rows")
print(f"2. DimProvider.csv: {len(dim_provider):,} rows")
print(f"3. DimDate.csv: {len(dim_date):,} rows")
print(f"4. FactAppointments.csv: {len(fact_appointments):,} rows")
print(f"5. FactBilling.csv: {len(fact_billing):,} rows")
print(f"6. FactReferrals.csv: {len(fact_referrals):,} rows")
print(f"7. FactReadmissions.csv: {len(fact_readmissions):,} rows")
print(f"8. FactSurveys.csv: {len(fact_surveys):,} rows")
print(f"9. FactPortalUsage.csv: {len(fact_portal_usage):,} rows")
print(f"10. FactComplaints.csv: {len(fact_complaints):,} rows")
print(f"11. FactTelehealth.csv: {len(fact_telehealth):,} rows")
print(f"12. FactInterpreter.csv: {len(fact_interpreter):,} rows")
print(f"\nTotal rows generated: {len(dim_patient) + len(dim_provider) + len(dim_date) + len(fact_appointments) + len(fact_billing) + len(fact_referrals) + len(fact_readmissions) + len(fact_surveys) + len(fact_portal_usage) + len(fact_complaints) + len(fact_telehealth) + len(fact_interpreter):,}")
print("\n✓ Ready to import into Power BI!")
print("="*60)