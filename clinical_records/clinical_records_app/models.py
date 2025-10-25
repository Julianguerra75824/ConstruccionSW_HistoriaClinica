from mongoengine import (
    Document, EmbeddedDocument, StringField, IntField, DateField, BooleanField,
    EmbeddedDocumentField, ListField, ReferenceField
)
from datetime import datetime

class Medication(EmbeddedDocument):
    medicine_id = IntField(required=True)
    dose = StringField(max_length=100)
    duration = StringField(max_length=100)
    item = StringField(max_length=100)

class MedicalProcedure(EmbeddedDocument):
    procedure_id = IntField(required=True)
    quantity = IntField(default=1)
    frequency = StringField(max_length=100)
    requires_specialist_assistance = BooleanField(default=False)
    specialist_id = StringField(max_length=50)
    item = StringField(max_length=100)

class DiagnosticHelp(EmbeddedDocument):
    diagnostic_help_id = IntField(required=True)
    quantity = IntField(default=1)
    requires_specialist_assistance = BooleanField(default=False)
    specialist_id = StringField(max_length=50)
    item = StringField(max_length=100)

class ClinicalRecord(Document):
    date = DateField(required=True)
    doctor_id = IntField(required=True)
    motive = StringField(max_length=200)
    symptoms = StringField(max_length=300)
    diagnosis = StringField(max_length=300)
    procedure_details = StringField()
    medications = ListField(EmbeddedDocumentField(Medication))
    medical_procedures = ListField(EmbeddedDocumentField(MedicalProcedure))
    diagnostic_helps = ListField(EmbeddedDocumentField(DiagnosticHelp))
    created_at = DateField(default=datetime.utcnow)
    updated_at = DateField(default=datetime.utcnow)

    meta = {
        "collection": "clinical_records",
        "indexes": ["doctor_id", "date"],
        "ordering": ["date"]
    }

    def __str__(self):
        return f"ClinicalRecord({self.id}) - Dr:{self.doctor_id} - {self.date}"

class Patient(Document):
    id = IntField(required=True, unique=True)
    clinical_records = ListField(ReferenceField(ClinicalRecord, reverse_delete_rule=2))  # CASCADE
    created_at = DateField(default=datetime.utcnow)

    meta = {
        "collection": "patients",
        "indexes": ["id"]
    }

    def __str__(self):
        return f"Patient({self.id})"
