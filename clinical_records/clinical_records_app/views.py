import datetime
import json
from django.shortcuts import render
from .models import DiagnosticHelp, MedicalProcedure, Medication, Patient, ClinicalRecord
from django.http import JsonResponse

def search_clinical_record(request):
    try:
        patients = Patient.objects.all()  # O podrías filtrar con .filter(...)
        
        data = []
        for p in patients:
            # Convertimos los registros clínicos a una lista legible
            clinical_records_data = []
            for record in p.clinical_records:
                clinical_records_data.append({
                    "id": str(record.id),
                    "date": record.date.isoformat() if record.date else None,
                    "doctor_id": record.doctor_id,
                    "motive": record.motive,
                    "diagnosis": record.diagnosis
                })

            data.append({
                "patient_id": p.patient_id,
                "clinical_records": clinical_records_data
            })
        
        return JsonResponse(data, safe=False, json_dumps_params={"ensure_ascii": False})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def create_clinical_record(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido. Usa POST."}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))

        required_fields = ["patient_id", "doctor_id", "date", "motive", "diagnosis"]
        for field in required_fields:
            if field not in data:
                return JsonResponse({"error": f"Campo requerido: {field}"}, status=400)

        patient_id = data["patient_id"]

        # ✅ Buscar paciente o crearlo automáticamente
        patient = Patient.objects(id=patient_id).first()
        if not patient:
            patient = Patient(id=patient_id)
            patient.save()

        # ✅ Procesar listas embebidas
        medications = [
            Medication(
                medicine_id=med.get("medicine_id"),
                dose=med.get("dose", ""),
                duration=med.get("duration", ""),
                item=med.get("item", "")
            )
            for med in data.get("medications", [])
        ]

        medical_procedures = [
            MedicalProcedure(
                procedure_id=proc.get("procedure_id"),
                quantity=proc.get("quantity", 1),
                frequency=proc.get("frequency", ""),
                requires_specialist_assistance=proc.get("requires_specialist_assistance", False),
                specialist_id=proc.get("specialist_id", ""),
                item=proc.get("item", "")
            )
            for proc in data.get("medical_procedures", [])
        ]

        diagnostic_helps = [
            DiagnosticHelp(
                diagnostic_help_id=diag.get("diagnostic_help_id"),
                quantity=diag.get("quantity", 1),
                requires_specialist_assistance=diag.get("requires_specialist_assistance", False),
                specialist_id=diag.get("specialist_id", ""),
                item=diag.get("item", "")
            )
            for diag in data.get("diagnostic_helps", [])
        ]

        # ✅ Crear registro clínico
        record = ClinicalRecord(
            date=datetime.fromisoformat(data["date"]),
            doctor_id=data["doctor_id"],
            motive=data["motive"],
            symptoms=data.get("symptoms", ""),
            diagnosis=data["diagnosis"],
            procedure_details=data.get("procedure_details", ""),
            medications=medications,
            medical_procedures=medical_procedures,
            diagnostic_helps=diagnostic_helps,
        )
        record.save()

        # ✅ Asociar al paciente
        patient.clinical_records.append(record)
        patient.save()

        return JsonResponse({
            "message": "Historia clínica creada correctamente.",
            "patient_id": patient.id,
            "clinical_record_id": str(record.id)
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)