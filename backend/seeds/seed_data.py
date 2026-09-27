import os
import sys
from datetime import date, datetime, timedelta, time, timezone
from decimal import Decimal
import random

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, engine, Base
from app.models.user import User, Dentist
from app.models.patient import Patient, MedicalHistory, DentalHistory
from app.models.appointment import Appointment, AppointmentType
from app.models.clinical import Visit
from app.models.dental_chart import ToothCondition, ToothConditionHistory, FDI_PERMANENT_TEETH
from app.models.treatment import TreatmentPlan, TreatmentItem, ProcedureCatalog
from app.models.prescription import Prescription, PrescriptionItem, MedicineCatalog
from app.models.billing import Invoice, InvoiceItem, Payment
from app.models.document import Document
from app.models.followup import FollowUp
from app.models.audit import AuditLog
from app.security.hashing import hash_password

def seed_database(db=None):
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True
    print("Seeding database with realistic dental clinic data...")

    # Clear existing if needed
    # (Safe reset)
    db.query(AuditLog).delete()
    db.query(Payment).delete()
    db.query(InvoiceItem).delete()
    db.query(Invoice).delete()
    db.query(Document).delete()
    db.query(FollowUp).delete()
    db.query(PrescriptionItem).delete()
    db.query(Prescription).delete()
    db.query(TreatmentItem).delete()
    db.query(TreatmentPlan).delete()
    db.query(ToothConditionHistory).delete()
    db.query(ToothCondition).delete()
    db.query(Visit).delete()
    db.query(Appointment).delete()
    db.query(AppointmentType).delete()
    db.query(MedicalHistory).delete()
    db.query(DentalHistory).delete()
    db.query(Patient).delete()
    db.query(Dentist).delete()
    db.query(User).delete()
    db.query(ProcedureCatalog).delete()
    db.query(MedicineCatalog).delete()
    db.commit()

    # 1. Procedure Catalog
    procedures_data = [
        ("CONS-01", "Comprehensive Oral Examination", "Preventive", Decimal('50.00'), "Full oral cavity checkup, soft tissue exam, periodontal probing"),
        ("CLEAN-01", "Dental Prophylaxis & Scaling", "Preventive", Decimal('90.00'), "Ultrasonic scaling and polishing for plaque/calculus removal"),
        ("FILL-COMP", "Composite Resin Filling (1-2 surfaces)", "Restorative", Decimal('120.00'), "Tooth-colored aesthetic resin restoration"),
        ("FILL-COMP-L", "Composite Resin Filling (Complex/MOD)", "Restorative", Decimal('180.00'), "Multi-surface composite restoration"),
        ("RCT-ANT", "Root Canal Therapy (Anterior)", "Endodontics", Decimal('350.00'), "Chemo-mechanical canal preparation, disinfection and obturation"),
        ("RCT-MOL", "Root Canal Therapy (Molar)", "Endodontics", Decimal('550.00'), "Multi-canal molar endodontic treatment"),
        ("CRN-PFM", "Porcelain-Fused-to-Metal (PFM) Crown", "Prosthodontics", Decimal('450.00'), "High strength PFM crown restoration"),
        ("CRN-ZIRC", "Zirconia Aesthetic Crown", "Prosthodontics", Decimal('650.00'), "Monolithic CAD/CAM zirconia crown"),
        ("EXT-SIMP", "Simple Tooth Extraction", "Surgery", Decimal('80.00'), "Routine forceps extraction with local anaesthesia"),
        ("EXT-SURG", "Surgical Extraction / Impaction", "Surgery", Decimal('220.00'), "Surgical elevation and bone guttering for impacted tooth"),
        ("XRAY-PA", "Periapical Digital Radiograph (IOPA)", "Diagnostic", Decimal('25.00'), "High resolution digital periapical sensor radiograph"),
        ("XRAY-OPG", "Panoramic Radiograph (OPG)", "Diagnostic", Decimal('60.00'), "Full mouth panoramic digital radiograph"),
        ("BLEACH-01", "In-Office Teeth Whitening", "Cosmetic", Decimal('300.00'), "LED accelerated bleaching treatment"),
    ]
    for code, name, cat, cost, desc in procedures_data:
        db.add(ProcedureCatalog(code=code, name=name, category=cat, default_cost=cost, description=desc))

    # 2. Medicine Catalog
    medicines_data = [
        ("Amoxicillin 500mg", "Amoxicillin", "Capsule", "500mg", "Take 1 capsule 3 times daily for 5-7 days after meals."),
        ("Augmentin 625mg", "Amoxicillin + Clavulanic Acid", "Tablet", "625mg", "Take 1 tablet twice daily with food for 5 days."),
        ("Ibuprofen 400mg", "Ibuprofen", "Tablet", "400mg", "Take 1 tablet every 8 hours as needed for dental pain/swelling."),
        ("Paracetamol 650mg", "Acetaminophen", "Tablet", "650mg", "Take 1 tablet every 6 hours for mild pain/fever."),
        ("Ketorolac 10mg", "Ketorolac Tromethamine", "Tablet", "10mg", "Take 1 tablet every 6 hours for severe acute pain (max 5 days)."),
        ("Metronidazole 400mg", "Metronidazole", "Tablet", "400mg", "Take 1 tablet 3 times daily for anaerobic odontogenic infection."),
        ("Chlorhexidine 0.2% Mouthwash", "Chlorhexidine Gluconate", "Mouthwash", "15ml", "Rinse mouth twice daily for 30-60 seconds for 7 days."),
        ("Triamcinolone Acetonide Oral Paste", "Triamcinolone", "Gel", "0.1%", "Apply small dab to aphthous ulcer before bedtime."),
    ]
    for name, gen, form, dose, inst in medicines_data:
        db.add(MedicineCatalog(name=name, generic_name=gen, dosage_form=form, default_dosage=dose, instructions=inst))

    # 3. Appointment Types
    app_types = [
        ("Routine Checkup & Consultation", 30, "#10b981", 50),
        ("Teeth Cleaning / Scaling", 45, "#06b6d4", 90),
        ("Filling / Restoration", 45, "#3b82f6", 120),
        ("Root Canal Treatment", 60, "#8b5cf6", 350),
        ("Extraction / Oral Surgery", 45, "#ef4444", 150),
        ("Crown Preparation & Fitting", 60, "#f59e0b", 450),
        ("Emergency Dental Care", 30, "#dc2626", 100),
    ]
    appt_type_objs = []
    for name, dur, col, fee in app_types:
        at = AppointmentType(name=name, duration_minutes=dur, color_code=col, default_fee=fee)
        db.add(at)
        appt_type_objs.append(at)

    # 4. Users (Admin, 2 Dentists, 2 Receptionists)
    pw_hash = hash_password("Dental@123")

    admin_user = User(
        email="admin@clinic.com",
        username="admin",
        hashed_password=pw_hash,
        full_name="Sarah Jenkins (Admin)",
        role="admin",
        phone="+1 555-0100",
        is_active=True
    )
    db.add(admin_user)

    dentist1_user = User(
        email="dr.chen@clinic.com",
        username="dr.chen",
        hashed_password=pw_hash,
        full_name="Dr. Marcus Chen",
        role="dentist",
        phone="+1 555-0201",
        is_active=True
    )
    db.add(dentist1_user)

    dentist2_user = User(
        email="dr.alvarez@clinic.com",
        username="dr.alvarez",
        hashed_password=pw_hash,
        full_name="Dr. Elena Alvarez",
        role="dentist",
        phone="+1 555-0202",
        is_active=True
    )
    db.add(dentist2_user)

    rec1_user = User(
        email="reception1@clinic.com",
        username="reception1",
        hashed_password=pw_hash,
        full_name="Jessica Miller",
        role="receptionist",
        phone="+1 555-0301",
        is_active=True
    )
    db.add(rec1_user)

    rec2_user = User(
        email="reception2@clinic.com",
        username="reception2",
        hashed_password=pw_hash,
        full_name="David Patel",
        role="receptionist",
        phone="+1 555-0302",
        is_active=True
    )
    db.add(rec2_user)
    db.flush()

    # Dentist profiles
    dentist1 = Dentist(
        user_id=dentist1_user.id,
        license_number="DEN-LIC-88231",
        specialization="Endodontics & Conservative Dentistry",
        qualifications="BDS, MDS (Endo)",
        cabin_number="Operatory 1",
        is_active=True
    )
    dentist2 = Dentist(
        user_id=dentist2_user.id,
        license_number="DEN-LIC-94102",
        specialization="Prosthodontics & Implantology",
        qualifications="BDS, MS (Prostho), FICOI",
        cabin_number="Operatory 2",
        is_active=True
    )
    db.add(dentist1)
    db.add(dentist2)
    db.flush()

    # 5. 16 Realistic Patients
    patients_data = [
        ("Liam", "Smith", date(1985, 4, 12), "Male", "+1 555-1011", "liam.smith@example.com", "742 Evergreen Terrace, Springfield", "Emma Smith", "+1 555-1012", "O+", "Penicillin allergy", "None", "None", "Toothache in upper right molar on chewing"),
        ("Olivia", "Johnson", date(1992, 8, 24), "Female", "+1 555-1021", "olivia.j@example.com", "124 Conch Street, Bikini", "Mark Johnson", "+1 555-1022", "A+", "None", "Hypertension", "Lisinopril 10mg", "Routine cleaning and checkup"),
        ("Noah", "Williams", date(1978, 11, 3), "Male", "+1 555-1031", "noah.w@example.com", "304 Elm Street, Riverdale", "Sophia Williams", "+1 555-1032", "B+", "Latex", "Type 2 Diabetes", "Metformin 500mg", "Bleeding gums while brushing"),
        ("Emma", "Brown", date(1995, 1, 15), "Female", "+1 555-1041", "emma.brown@example.com", "89 Maple Ave, Greenfield", "Lucas Brown", "+1 555-1042", "AB+", "Sulfa drugs", "Asthma", "Albuterol inhaler", "Chipped lower front tooth from accident"),
        ("James", "Jones", date(1964, 6, 30), "Male", "+1 555-1051", "james.j@example.com", "412 Oak Lane, Lakeside", "Mary Jones", "+1 555-1052", "O-", "Aspirin", "Cardiovascular disease", "Atorvastatin 20mg", "Needs crown for missing tooth"),
        ("Sophia", "Garcia", date(2001, 9, 18), "Female", "+1 555-1061", "sophia.g@example.com", "55 Pine Ridge, Hilltop", "Carlos Garcia", "+1 555-1062", "A-", "None", "None", "None", "Wisdom tooth pain in lower jaw"),
        ("Benjamin", "Miller", date(1989, 12, 5), "Male", "+1 555-1071", "ben.miller@example.com", "77 Forest Court, Woodside", "Chloe Miller", "+1 555-1072", "B-", "None", "None", "None", "Sensitivity to cold water on lower left"),
        ("Isabella", "Davis", date(1998, 3, 22), "Female", "+1 555-1081", "isabella.d@example.com", "101 Ocean Blvd, Bayview", "Ethan Davis", "+1 555-1082", "O+", "None", "Mild Anemia", "Iron supplements", "Wants teeth whitening for wedding"),
        ("Lucas", "Rodriguez", date(1973, 7, 14), "Male", "+1 555-1091", "lucas.r@example.com", "230 Sunset Dr, Palms", "Ana Rodriguez", "+1 555-1092", "AB-", "Codeine", "GERD", "Omeprazole 20mg", "Loose lower molar"),
        ("Mia", "Martinez", date(1990, 5, 29), "Female", "+1 555-1101", "mia.m@example.com", "410 Cedar Way, Fairview", "Diego Martinez", "+1 555-1102", "A+", "None", "Hypothyroidism", "Levothyroxine 50mcg", "Old silver filling fell out"),
        ("Henry", "Hernandez", date(1982, 10, 8), "Male", "+1 555-1111", "henry.h@example.com", "882 Birch St, Highwood", "Elena Hernandez", "+1 555-1112", "O+", "None", "None", "None", "General consultation & staining"),
        ("Harper", "Lopez", date(1994, 2, 17), "Female", "+1 555-1121", "harper.l@example.com", "315 Willow Terrace, Brookside", "Daniel Lopez", "+1 555-1122", "B+", "Amoxicillin", "Migraine", "Sumatriptan PRN", "Discoloration of front teeth"),
        ("Alexander", "Gonzalez", date(1969, 8, 11), "Male", "+1 555-1131", "alex.g@example.com", "620 Sycamore Ave, Plainfield", "Grace Gonzalez", "+1 555-1132", "A+", "None", "High Cholesterol", "Rosuvastatin 10mg", "Severe throbbing pain keeping awake at night"),
        ("Evelyn", "Wilson", date(1987, 12, 27), "Female", "+1 555-1141", "evelyn.w@example.com", "154 Walnut Rd, Crestview", "Ryan Wilson", "+1 555-1142", "O-", "None", "None", "None", "Bleeding gums and bad breath"),
        ("Daniel", "Anderson", date(2003, 4, 19), "Male", "+1 555-1151", "daniel.a@example.com", "901 Chestnut St, Summit", "Karen Anderson", "+1 555-1152", "AB+", "None", "None", "None", "Mild sensitivity on upper premolars"),
        ("Charlotte", "Thomas", date(1996, 7, 7), "Female", "+1 555-1161", "charlotte.t@example.com", "478 Magnolia St, Gardens", "Samuel Thomas", "+1 555-1162", "B+", "None", "None", "None", "Routine 6-month checkup and polish")
    ]

    patient_objs = []
    for idx, (fn, ln, dob, gen, ph, em, addr, ec_name, ec_ph, bg, allergy, med_cond, meds, complaint) in enumerate(patients_data, start=1001):
        p = Patient(
            patient_code=f"P-{idx}",
            first_name=fn,
            last_name=ln,
            date_of_birth=dob,
            gender=gen,
            phone=ph,
            email=em,
            address=addr,
            emergency_contact_name=ec_name,
            emergency_contact_phone=ec_ph,
            blood_group=bg,
            is_deleted=False,
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(5, 60))
        )
        db.add(p)
        db.flush()

        med_h = MedicalHistory(
            patient_id=p.id,
            allergies=allergy,
            medical_conditions=med_cond,
            current_medications=meds,
            bleeding_disorders=False,
            is_pregnant=False,
            notes="Annual update confirmed."
        )
        db.add(med_h)

        dent_h = DentalHistory(
            patient_id=p.id,
            chief_complaint=complaint,
            brushing_frequency="Twice daily",
            flossing=random.choice([True, False]),
            habits="None",
            dental_anxiety_level=random.choice(["None", "Mild", "Moderate"]),
            notes="Patient cooperative during examination."
        )
        db.add(dent_h)
        patient_objs.append(p)

    db.commit()

    # 6. Appointments (Past, Today, Upcoming)
    today = date.today()
    created_appts = []

    # Past appointments
    past_appts_data = [
        (patient_objs[0], dentist1, today - timedelta(days=7), time(9, 30), time(10, 0), "completed", "Severe toothache in upper right", appt_type_objs[0]),
        (patient_objs[1], dentist2, today - timedelta(days=5), time(10, 0), time(10, 45), "completed", "Routine scaling & polishing", appt_type_objs[1]),
        (patient_objs[2], dentist1, today - timedelta(days=3), time(14, 0), time(14, 45), "completed", "Bleeding gums evaluation", appt_type_objs[0]),
        (patient_objs[3], dentist2, today - timedelta(days=2), time(11, 0), time(12, 0), "completed", "Chipped tooth aesthetic restoration", appt_type_objs[2]),
        (patient_objs[4], dentist2, today - timedelta(days=1), time(15, 0), time(16, 0), "completed", "Crown prep consultation", appt_type_objs[5]),
    ]
    for p, d, adate, st, et, st_name, rsn, atype in past_appts_data:
        appt = Appointment(
            patient_id=p.id,
            dentist_id=d.id,
            appointment_type_id=atype.id,
            appointment_date=adate,
            start_time=st,
            end_time=et,
            status=st_name,
            reason=rsn
        )
        db.add(appt)
        created_appts.append(appt)

    # Today's appointments
    today_appts_data = [
        (patient_objs[5], dentist1, today, time(9, 0), time(9, 30), "confirmed", "Wisdom tooth evaluation", appt_type_objs[4]),
        (patient_objs[6], dentist1, today, time(10, 0), time(10, 45), "in_progress", "Sensitivity treatment on tooth 36", appt_type_objs[2]),
        (patient_objs[7], dentist2, today, time(11, 0), time(12, 0), "confirmed", "Teeth whitening session", appt_type_objs[1]),
        (patient_objs[8], dentist2, today, time(14, 30), time(15, 15), "scheduled", "Mobility assessment", appt_type_objs[0]),
    ]
    for p, d, adate, st, et, st_name, rsn, atype in today_appts_data:
        appt = Appointment(
            patient_id=p.id,
            dentist_id=d.id,
            appointment_type_id=atype.id,
            appointment_date=adate,
            start_time=st,
            end_time=et,
            status=st_name,
            reason=rsn
        )
        db.add(appt)
        created_appts.append(appt)

    # Future appointments
    future_appts_data = [
        (patient_objs[0], dentist1, today + timedelta(days=2), time(10, 0), time(11, 0), "scheduled", "RCT Step 2 on tooth 16", appt_type_objs[3]),
        (patient_objs[9], dentist1, today + timedelta(days=3), time(11, 30), time(12, 15), "scheduled", "Filling replacement", appt_type_objs[2]),
        (patient_objs[10], dentist2, today + timedelta(days=4), time(9, 30), time(10, 15), "scheduled", "Checkup and scaling", appt_type_objs[1]),
        (patient_objs[11], dentist2, today + timedelta(days=5), time(15, 0), time(15, 45), "scheduled", "Veneer consultation", appt_type_objs[0]),
        (patient_objs[12], dentist1, today + timedelta(days=6), time(14, 0), time(15, 0), "scheduled", "Emergency root canal", appt_type_objs[6]),
    ]
    for p, d, adate, st, et, st_name, rsn, atype in future_appts_data:
        appt = Appointment(
            patient_id=p.id,
            dentist_id=d.id,
            appointment_type_id=atype.id,
            appointment_date=adate,
            start_time=st,
            end_time=et,
            status=st_name,
            reason=rsn
        )
        db.add(appt)
        created_appts.append(appt)

    db.commit()

    # 7. Completed Visits & Examinations
    visits = []
    # Visit 1: Liam Smith (tooth 16 acute irreversible pulpitis)
    v1 = Visit(
        patient_id=patient_objs[0].id,
        dentist_id=dentist1.id,
        appointment_id=created_appts[0].id,
        visit_date=today - timedelta(days=7),
        vitals_blood_pressure="122/78",
        vitals_pulse=74,
        chief_complaint="Severe continuous throbbing pain in upper right back tooth (16) aggravated by hot beverages.",
        oral_findings="Deep occlusal disto-occlusal caries on tooth 16 extending into pulp chamber. Tenderness to vertical percussion positive.",
        gum_condition="Mild localized gingival erythema around 16.",
        hygiene_index="Fair",
        diagnosis="Acute Irreversible Pulpitis with Symptomatic Apical Periodontitis - Tooth 16",
        clinical_notes="Emergency pulpectomy performed. Canal working lengths determined. Calcium hydroxide intracanal medicament placed. Temporary restoration with Cavit."
    )
    db.add(v1)

    # Visit 2: Olivia Johnson (prophylaxis)
    v2 = Visit(
        patient_id=patient_objs[1].id,
        dentist_id=dentist2.id,
        appointment_id=created_appts[1].id,
        visit_date=today - timedelta(days=5),
        vitals_blood_pressure="128/82",
        vitals_pulse=70,
        chief_complaint="Routine 6-month checkup and prophylaxis.",
        oral_findings="Supragingival calculus and extrinsic tea staining on lingual surfaces of lower anterior teeth (31-33, 41-43). No cavitation detected.",
        gum_condition="Generalized mild marginal gingivitis without attachment loss.",
        hygiene_index="Good",
        diagnosis="Plaque-induced generalized mild gingivitis.",
        clinical_notes="Full mouth ultrasonic scaling completed followed by fine grit prophy paste polish. Flossing technique demonstrated."
    )
    db.add(v2)

    # Visit 3: Emma Brown (chipped incisor)
    v3 = Visit(
        patient_id=patient_objs[3].id,
        dentist_id=dentist2.id,
        appointment_id=created_appts[3].id,
        visit_date=today - timedelta(days=2),
        vitals_blood_pressure="116/74",
        vitals_pulse=76,
        chief_complaint="Incisal edge fracture of tooth 11 following a sports collision.",
        oral_findings="Class IV Ellis Class II enamel-dentin fracture of mesio-incisal angle on tooth 11 without pulpal exposure. Vitality test positive.",
        gum_condition="Healthy pink stippled gingiva.",
        hygiene_index="Good",
        diagnosis="Ellis Class II Uncomplicated Crown Fracture - Tooth 11",
        clinical_notes="Enamel bevel placed. 37% phosphoric acid etch for 15s. Single-bond universal adhesive applied and cured. Multi-shade composite resin (Filtek Supreme A2B/A1E) layered and polished to high gloss."
    )
    db.add(v3)
    db.commit()

    # 8. FDI Tooth Conditions (Permanent Teeth 11-48)
    # Populate full 32 teeth for patient 0, 1, 3
    for p in patient_objs:
        for t_num in FDI_PERMANENT_TEETH:
            cond = "healthy"
            sev = "none"
            surf = None
            notes = None

            # Add specific realistic dental conditions
            if p == patient_objs[0]: # Liam Smith
                if t_num == 16:
                    cond = "root_canal"
                    sev = "severe"
                    surf = "MOD"
                    notes = "Under active endodontic therapy."
                elif t_num == 18:
                    cond = "missing"
                    notes = "Extracted 3 years ago."
                elif t_num == 26:
                    cond = "filled"
                    surf = "O"
                    notes = "Composite filling intact."
                elif t_num == 36:
                    cond = "caries"
                    sev = "mild"
                    surf = "O"
                    notes = "Incipient pit and fissure caries."
            elif p == patient_objs[3]: # Emma Brown
                if t_num == 11:
                    cond = "filled"
                    surf = "MI"
                    notes = "Class IV composite restoration."
                elif t_num == 46:
                    cond = "crown"
                    notes = "Full zirconia crown placed 2022."
            elif p == patient_objs[4]: # James Jones
                if t_num == 46:
                    cond = "missing"
                    notes = "Missing tooth - recommended implant or bridge."
                elif t_num == 47:
                    cond = "crown"
                elif t_num == 37:
                    cond = "filled"

            tc = ToothCondition(
                patient_id=p.id,
                tooth_number=t_num,
                current_condition=cond,
                severity=sev,
                surfaces=surf,
                notes=notes
            )
            db.add(tc)

    # History entries
    h1 = ToothConditionHistory(
        patient_id=patient_objs[0].id,
        visit_id=v1.id,
        dentist_id=dentist1.id,
        tooth_number=16,
        condition="caries",
        severity="severe",
        surfaces="MOD",
        notes="Deep pulpal involvement noted."
    )
    h2 = ToothConditionHistory(
        patient_id=patient_objs[0].id,
        visit_id=v1.id,
        dentist_id=dentist1.id,
        tooth_number=16,
        condition="root_canal",
        severity="moderate",
        surfaces="MOD",
        notes="Pulpectomy completed. Intracanal dressing placed."
    )
    db.add(h1)
    db.add(h2)
    db.commit()

    # 9. Treatment Plans & Items
    # Plan 1: Liam Smith Root Canal + Crown
    tp1 = TreatmentPlan(
        patient_id=patient_objs[0].id,
        dentist_id=dentist1.id,
        title="Comprehensive Molar Endodontic & Restorative Plan",
        status="active",
        estimated_total=Decimal('1000.00'),
        notes="Includes 3-visit RCT, post-endodontic core build-up, and monolithic Zirconia crown."
    )
    db.add(tp1)
    db.flush()

    ti1 = TreatmentItem(
        treatment_plan_id=tp1.id,
        procedure_name="Root Canal Therapy (Molar)",
        tooth_number=16,
        estimated_cost=Decimal('550.00'),
        actual_cost=Decimal('550.00'),
        status="in_progress",
        visit_id=v1.id,
        notes="Canals located: MB1, MB2, DB, Palatal. Working length verified by apex locator."
    )
    ti2 = TreatmentItem(
        treatment_plan_id=tp1.id,
        procedure_name="Zirconia Aesthetic Crown",
        tooth_number=16,
        estimated_cost=Decimal('450.00'),
        actual_cost=Decimal('0.00'),
        status="planned",
        notes="Scheduled after obturation and core buildup."
    )
    db.add(ti1)
    db.add(ti2)

    # Plan 2: Emma Brown Front Tooth Aesthetics
    tp2 = TreatmentPlan(
        patient_id=patient_objs[3].id,
        dentist_id=dentist2.id,
        title="Anterior Aesthetic Restoration",
        status="completed",
        estimated_total=Decimal('180.00'),
        notes="Class IV composite build-up."
    )
    db.add(tp2)
    db.flush()

    ti3 = TreatmentItem(
        treatment_plan_id=tp2.id,
        procedure_name="Composite Resin Filling (Complex/MOD)",
        tooth_number=11,
        estimated_cost=Decimal('180.00'),
        actual_cost=Decimal('180.00'),
        status="completed",
        visit_id=v3.id,
        completed_at=datetime.now(timezone.utc) - timedelta(days=2),
        notes="Aesthetic restoration completed."
    )
    db.add(ti3)
    db.commit()

    # 10. Prescriptions
    rx1 = Prescription(
        prescription_number="RX-2026-1001",
        patient_id=patient_objs[0].id,
        dentist_id=dentist1.id,
        visit_id=v1.id,
        diagnosis_summary="Acute Pulpitis & Periapical Abscess - Tooth 16",
        general_instructions="Complete entire antibiotic course. Take pain relief with food. Avoid chewing hard items on upper right side."
    )
    db.add(rx1)
    db.flush()

    rxi1 = PrescriptionItem(
        prescription_id=rx1.id,
        medicine_name="Augmentin 625mg",
        dosage="625 mg",
        frequency="1-0-1 (Twice daily)",
        duration="5 days",
        timing="After Food",
        instructions="Complete full 5-day course."
    )
    rxi2 = PrescriptionItem(
        prescription_id=rx1.id,
        medicine_name="Ibuprofen 400mg",
        dosage="400 mg",
        frequency="1-0-1 (Twice daily)",
        duration="3 days",
        timing="After Food",
        instructions="For moderate dental pain."
    )
    rxi3 = PrescriptionItem(
        prescription_id=rx1.id,
        medicine_name="Chlorhexidine 0.2% Mouthwash",
        dosage="15 ml",
        frequency="Twice daily",
        duration="7 days",
        timing="After Brushing",
        instructions="Swish for 60 seconds and spit out."
    )
    db.add(rxi1)
    db.add(rxi2)
    db.add(rxi3)
    db.commit()

    # 11. Invoices & Payments
    # Invoice 1: Liam Smith
    inv1 = Invoice(
        invoice_number="INV-2026-1001",
        patient_id=patient_objs[0].id,
        visit_id=v1.id,
        treatment_plan_id=tp1.id,
        issue_date=today - timedelta(days=7),
        due_date=today + timedelta(days=7),
        subtotal=Decimal('625.00'),
        discount=Decimal('25.00'),
        tax=Decimal('0.00'),
        total=Decimal('600.00'),
        paid_amount=Decimal('400.00'),
        balance=Decimal('200.00'),
        status="partially_paid",
        notes="Consultation + Digital X-ray + Pulpectomy stage."
    )
    db.add(inv1)
    db.flush()

    ii1 = InvoiceItem(invoice_id=inv1.id, description="Emergency Consultation & Exam", unit_price=Decimal('50.00'), quantity=1, total=Decimal('50.00'))
    ii2 = InvoiceItem(invoice_id=inv1.id, description="Periapical Digital Radiograph (IOPA)", unit_price=Decimal('25.00'), quantity=1, total=Decimal('25.00'))
    ii3 = InvoiceItem(invoice_id=inv1.id, description="Root Canal Treatment Initiation (Tooth 16)", unit_price=Decimal('550.00'), quantity=1, total=Decimal('550.00'))
    db.add(ii1)
    db.add(ii2)
    db.add(ii3)

    pay1 = Payment(
        invoice_id=inv1.id,
        patient_id=patient_objs[0].id,
        amount=Decimal('400.00'),
        payment_method="card",
        transaction_reference="AUTH-TXN-994821",
        payment_date=datetime.now(timezone.utc) - timedelta(days=7),
        notes="Card payment swipe at front desk.",
        received_by_user_id=rec1_user.id
    )
    db.add(pay1)

    # Invoice 2: Olivia Johnson (Paid in full)
    inv2 = Invoice(
        invoice_number="INV-2026-1002",
        patient_id=patient_objs[1].id,
        visit_id=v2.id,
        issue_date=today - timedelta(days=5),
        due_date=today - timedelta(days=5),
        subtotal=Decimal('140.00'),
        discount=Decimal('0.00'),
        tax=Decimal('0.00'),
        total=Decimal('140.00'),
        paid_amount=Decimal('140.00'),
        balance=Decimal('0.00'),
        status="paid",
        notes="Oral exam + scaling."
    )
    db.add(inv2)
    db.flush()

    ii4 = InvoiceItem(invoice_id=inv2.id, description="Comprehensive Oral Examination", unit_price=Decimal('50.00'), quantity=1, total=Decimal('50.00'))
    ii5 = InvoiceItem(invoice_id=inv2.id, description="Dental Prophylaxis & Scaling", unit_price=Decimal('90.00'), quantity=1, total=Decimal('90.00'))
    db.add(ii4)
    db.add(ii5)

    pay2 = Payment(
        invoice_id=inv2.id,
        patient_id=patient_objs[1].id,
        amount=Decimal('140.00'),
        payment_method="upi",
        transaction_reference="UPI-REF-238491",
        payment_date=datetime.now(timezone.utc) - timedelta(days=5),
        notes="Instant mobile payment received.",
        received_by_user_id=rec1_user.id
    )
    db.add(pay2)

    # Invoice 3: Emma Brown (Paid in full)
    inv3 = Invoice(
        invoice_number="INV-2026-1003",
        patient_id=patient_objs[3].id,
        visit_id=v3.id,
        issue_date=today - timedelta(days=2),
        due_date=today - timedelta(days=2),
        subtotal=Decimal('205.00'),
        discount=Decimal('5.00'),
        tax=Decimal('0.00'),
        total=Decimal('200.00'),
        paid_amount=Decimal('200.00'),
        balance=Decimal('0.00'),
        status="paid"
    )
    db.add(inv3)
    db.flush()

    ii6 = InvoiceItem(invoice_id=inv3.id, description="Digital IOPA X-Ray (11)", unit_price=Decimal('25.00'), quantity=1, total=Decimal('25.00'))
    ii7 = InvoiceItem(invoice_id=inv3.id, description="Class IV Aesthetic Composite Restoration", unit_price=Decimal('180.00'), quantity=1, total=Decimal('180.00'))
    db.add(ii6)
    db.add(ii7)

    pay3 = Payment(
        invoice_id=inv3.id,
        patient_id=patient_objs[3].id,
        amount=Decimal('200.00'),
        payment_method="cash",
        payment_date=datetime.now(timezone.utc) - timedelta(days=2),
        notes="Cash payment received in full.",
        received_by_user_id=rec2_user.id
    )
    db.add(pay3)
    db.commit()

    # 12. Follow-ups
    fu1 = FollowUp(
        patient_id=patient_objs[0].id,
        dentist_id=dentist1.id,
        visit_id=v1.id,
        scheduled_date=today + timedelta(days=2),
        reason="Evaluate symptom relief & canal obturation (Tooth 16)",
        status="pending",
        notes="Check if percussion tenderness has subsided."
    )
    fu2 = FollowUp(
        patient_id=patient_objs[1].id,
        dentist_id=dentist2.id,
        visit_id=v2.id,
        scheduled_date=today + timedelta(days=180),
        reason="Routine 6-month periodontal maintenance",
        status="pending"
    )
    db.add(fu1)
    db.add(fu2)

    # 13. Audit logs sample
    audit_samples = [
        ("LOGIN", admin_user, "System", "admin", "Admin session established"),
        ("CREATE", rec1_user, "Patient", str(patient_objs[0].id), "Registered Liam Smith (P-1001)"),
        ("CREATE", rec1_user, "Appointment", str(created_appts[0].id), "Booked appointment for Liam Smith"),
        ("CREATE", dentist1_user, "Visit", str(v1.id), "Recorded clinical examination for tooth 16"),
        ("TOOTH_UPDATE", dentist1_user, "ToothCondition", f"{patient_objs[0].id}-16", "Updated tooth 16 to root_canal (severe)"),
        ("PRESCRIPTION_CREATE", dentist1_user, "Prescription", str(rx1.id), "Issued RX-2026-1001 (3 items)"),
        ("INVOICE_CREATE", rec1_user, "Invoice", str(inv1.id), "Generated invoice INV-2026-1001 ($600.00)"),
        ("PAYMENT_CREATE", rec1_user, "Payment", str(pay1.id), "Recorded $400.00 card payment"),
    ]
    for action, usr, ent_name, ent_id, detail in audit_samples:
        db.add(AuditLog(
            user_id=usr.id,
            user_email=usr.email,
            action=action,
            entity_name=ent_name,
            entity_id=ent_id,
            details=detail,
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) DemoSeeder/1.0",
            created_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48))
        ))

    db.commit()
    if should_close:
        db.close()
    print("Seeding successfully completed!")

if __name__ == "__main__":
    seed_database()
