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
        leads = session.query(Lead).filter(Lead.workorder_id == workorder_id).all()
        leads_data = [
            sanitize_for_json({
                "id": lead.id,
                "data": lead.data,
                "cluster_id": lead.cluster_id,
                "buyer_persona": lead.buyer_persona,
                "raw_webpage_text": lead.raw_webpage_text,
                "company_name": lead.company_name,
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
        for order, lead_id in enumerate(lead_ids):
            lead = session.query(Lead).filter(Lead.id == lead_id, Lead.workorder_id == workorder_id).first()
            if lead:
                lead.display_order = order
        session.commit()
        return {"success": True}
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