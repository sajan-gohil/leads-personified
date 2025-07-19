from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Workorder, Lead
import os
import shutil
import pandas as pd
import array
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from typing import List
from app.services.lead_processing import process_lead, cluster_lead_embeddings
import math
import numpy as np

DATABASE_URL = 'sqlite:///./workorders.db'
UPLOAD_DIR = './uploaded_files'

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/workorders")
def list_workorders():
    session = SessionLocal()
    try:
        workorders = session.query(Workorder).all()
        result = [
            {
                "id": w.id,
                "filename": w.filename,
                "upload_date": w.upload_date,
                "status": w.status
            } for w in workorders
        ]
        return result
    finally:
        session.close()

@app.post("/workorders/upload")
def upload_workorder(file: UploadFile = File(...)):
    session = SessionLocal()
    try:
        # Save file
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # Parse file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_location)
        else:
            df = pd.read_excel(file_location)
        # Create workorder
        workorder = Workorder(
            filename=file.filename,
            original_file_path=file_location,
            status='uploaded'
        )
        session.add(workorder)
        session.commit()
        # Add leads
        leads = []
        for _, row in df.iterrows():
            lead_data = row.to_dict()
            raw_text, buyer_persona, buyer_persona_embedding = process_lead(lead_data)
            company_name = extract_company_name(lead_data)
            lead = Lead(
                workorder_id=workorder.id,
                data=lead_data,
                raw_webpage_text=raw_text,
                buyer_persona=buyer_persona,
                buyer_persona_embedding=buyer_persona_embedding,
                company_name=company_name
            )
            session.add(lead)
            leads.append(lead)
        session.commit()
        # Run clustering and save cluster ids
        embeddings = [lead.buyer_persona_embedding for lead in leads]
        labels = cluster_lead_embeddings(embeddings)
        for lead, label in zip(leads, labels):
            lead.cluster_id = int(label)
        session.commit()
        return {"id": workorder.id, "filename": workorder.filename}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()

def sanitize_for_json(obj):
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, float):
        if math.isfinite(obj):
            return obj
        else:
            return None  # or str(obj)
    else:
        return obj

@app.get("/workorders/{workorder_id}")
def get_workorder(workorder_id: int):
    session = SessionLocal()
    try:
        workorder = session.query(Workorder).filter(Workorder.id == workorder_id).first()
        if not workorder:
            raise HTTPException(status_code=404, detail="Workorder not found")
        leads = session.query(Lead).filter(Lead.workorder_id == workorder_id).order_by(Lead.display_order.asc().nullslast(), Lead.id.asc()).all()
        leads_data = [
            sanitize_for_json({
                "id": lead.id,
                "data": lead.data,
                "cluster_id": lead.cluster_id,
                "buyer_persona": lead.buyer_persona,
                "raw_webpage_text": lead.raw_webpage_text,
                "company_name": lead.company_name,
                "status": lead.status or 'unchecked',
            })
            for lead in leads
        ]
        return {
            "id": workorder.id,
            "filename": workorder.filename,
            "upload_date": workorder.upload_date,
            "status": workorder.status,
            "leads": leads_data
        }
    finally:
        session.close()

@app.post("/workorders/{workorder_id}/rerank")
def persist_rerank(workorder_id: int, lead_ids: list = Body(...)):
    session = SessionLocal()
    try:
        # Fetch all leads for this workorder
        leads = session.query(Lead).filter(Lead.workorder_id == workorder_id).all()
        # Separate leads by status
        converted_leads = [lead for lead in leads if lead.status == 'converted' and lead.buyer_persona_embedding is not None]
        failed_leads = [lead for lead in leads if lead.status == 'failed' and lead.buyer_persona_embedding is not None]
        inprogress_leads = [lead for lead in leads if lead.status == 'in-progress' and lead.buyer_persona_embedding is not None]
        unchecked_leads = [lead for lead in leads if (lead.status == 'unchecked' or not lead.status) and lead.buyer_persona_embedding is not None]


        def to_np(embedding):
            import numpy as np
            if isinstance(embedding, (bytes, bytearray)):
                return np.frombuffer(embedding, dtype=np.float32)
            elif isinstance(embedding, np.ndarray):
                return embedding
            else:
                return np.array(embedding, dtype=np.float32)

        def cosine_similarity(a, b):
            import numpy as np
            if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
                return 0.0
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

        # Prepare embeddings for converted
        converted_embeddings = [(lead, to_np(lead.buyer_persona_embedding)) for lead in converted_leads]

        # For each unchecked lead, compute similarity to closest converted lead
        lead_scores = []
        for lead in unchecked_leads:
            emb = to_np(lead.buyer_persona_embedding)
            if not converted_embeddings:
                score = 0.0
            else:
                score = max([cosine_similarity(emb, conv_emb) for _, conv_emb in converted_embeddings])
            lead_scores.append((lead, score))

        # Sort unchecked by similarity descending
        lead_scores.sort(key=lambda x: x[1], reverse=True)
        sorted_unchecked = [lead for lead, _ in lead_scores]

        # For converted, failed, in-progress: keep their previous display_order, sort by it
        def by_display_order(lead):
            return lead.display_order if lead.display_order is not None else 99999

        sorted_converted = sorted(converted_leads, key=by_display_order)
        sorted_failed = sorted(failed_leads, key=by_display_order)
        sorted_inprogress = sorted(inprogress_leads, key=by_display_order)

        # New order: unchecked first, then converted, in-progress, failed
        new_order = sorted_unchecked + sorted_converted + sorted_inprogress + sorted_failed

        # Update display_order
        for order, lead in enumerate(new_order):
            lead.display_order = order
        session.commit()
        return {"success": True, "reranked": [{"id": lead.id, "status": lead.status, "display_order": lead.display_order} for lead in new_order]}
    finally:
        session.close()

@app.post("/workorders/{workorder_id}/leads/{lead_id}/status")
def update_lead_status(workorder_id: int, lead_id: int, status_data: dict = Body(...)):
    session = SessionLocal()
    try:
        lead = session.query(Lead).filter(Lead.id == lead_id, Lead.workorder_id == workorder_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        new_status = status_data.get('status')
        if new_status not in ['unchecked', 'converted', 'failed', 'in-progress']:
            raise HTTPException(status_code=400, detail="Invalid status value")
        
        lead.status = new_status
        session.commit()
        return {"success": True, "lead_id": lead_id, "status": new_status}
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@app.post("/workorders/{workorder_id}/leads/status/batch")
def update_multiple_lead_statuses(workorder_id: int, status_updates: dict = Body(...)):
    """Update multiple lead statuses at once"""
    session = SessionLocal()
    try:
        updated_leads = []
        for lead_index, status in status_updates.items():
            if status not in ['unchecked', 'converted', 'failed', 'in-progress']:
                continue
            
            # Find lead by workorder_id and original index position
            leads = session.query(Lead).filter(Lead.workorder_id == workorder_id).order_by(Lead.id).all()
            try:
                lead_idx = int(lead_index)
                if 0 <= lead_idx < len(leads):
                    lead = leads[lead_idx]
                    lead.status = status
                    updated_leads.append({"lead_id": lead.id, "index": lead_idx, "status": status})
            except (ValueError, IndexError):
                continue
        
        session.commit()
        return {"success": True, "updated_leads": updated_leads}
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

def extract_company_name(data):
    # Try common keys for company name
    for key in data.keys():
        if key.lower() in ["company", "company name", "organisation", "organization", "business", "firm"]:
            return data[key]
    # Fallback: first string value
    for v in data.values():
        if isinstance(v, str) and v.strip():
            return v
    return "" 