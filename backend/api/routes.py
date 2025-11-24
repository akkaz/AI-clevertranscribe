import shutil
import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.services.transcription_service import TranscriptionService
from backend.services.analysis_service import AnalysisService
from backend.database import get_db, Job, Client, init_db

# Initialize DB
init_db()

router = APIRouter()

class JobStatus:
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobResult(BaseModel):
    transcription: Optional[str] = None
    analysis: Optional[dict] = None

class JobResponse(BaseModel):
    job_id: str
    status: str
    filename: str
    semantic_title: Optional[str] = None
    result: Optional[JobResult] = None
    error: Optional[str] = None
    created_at: str
    client_name: Optional[str] = None

    class Config:
        from_attributes = True

class ClientCreate(BaseModel):
    name: str

class ClientResponse(BaseModel):
    id: str
    name: str
    created_at: str
    
    class Config:
        from_attributes = True

class ToDoUpdate(BaseModel):
    index: int
    done: bool

def process_transcription(job_id: str, file_path: str, language: str, model: str, custom_prompt: Optional[str]):
    db = next(get_db())
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        return

    job.status = JobStatus.PROCESSING
    db.commit()

    try:
        # Transcribe
        transcription_service = TranscriptionService()
        text = transcription_service.process_file(file_path, language)
        
        # Analyze
        analysis_service = AnalysisService()
        analysis = analysis_service.analyze_transcription(text, model, custom_prompt)
        
        # Generate semantic title
        semantic_title = analysis_service.generate_title(text)
        
        job.transcription = text
        job.semantic_title = semantic_title
        job.analysis_report = analysis.get("report")
        
        # Convert simple string list to object list for checkboxes
        raw_todos = analysis.get("todo_list", [])
        if raw_todos and isinstance(raw_todos[0], str):
            job.analysis_todo = [{"text": item, "done": False} for item in raw_todos]
        else:
            job.analysis_todo = []
            
        job.status = JobStatus.COMPLETED
        db.commit()
        
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error = str(e)
        db.commit()
    finally:
        # Cleanup uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
        db.close()

# --- Client Routes ---

@router.post("/clients", response_model=ClientResponse)
async def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    print(f"Creating client: {client.name}")
    try:
        # Check if exists
        existing = db.query(Client).filter(Client.name == client.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Client already exists")
        
        new_client = Client(id=str(uuid.uuid4()), name=client.name)
        db.add(new_client)
        db.commit()
        db.refresh(new_client)
        print("Client created successfully")
        
        return ClientResponse(
            id=new_client.id,
            name=new_client.name,
            created_at=new_client.created_at.isoformat()
        )
    except Exception as e:
        print(f"Error creating client: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clients", response_model=List[ClientResponse])
async def list_clients(db: Session = Depends(get_db)):
    clients = db.query(Client).order_by(Client.name).all()
    return [ClientResponse(
        id=c.id,
        name=c.name,
        created_at=c.created_at.isoformat()
    ) for c in clients]

@router.delete("/clients/{client_id}")
async def delete_client(client_id: str, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return {"message": "Client deleted"}

# --- Job Routes ---

@router.post("/transcribe", response_model=JobResponse)
async def create_transcription_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = Form("it"),
    model: str = Form("gpt-4o"),
    custom_prompt: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{job_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    new_job = Job(
        id=job_id,
        filename=file.filename,
        status=JobStatus.QUEUED,
        language=language,
        model=model,
        custom_prompt=custom_prompt,
        client_id=client_id
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    background_tasks.add_task(process_transcription, job_id, file_path, language, model, custom_prompt)
    
    return map_job_to_response(new_job)

@router.patch("/jobs/{job_id}/todo")
async def update_todo_item(job_id: str, update: ToDoUpdate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    todos = list(job.analysis_todo) # Copy
    if update.index < 0 or update.index >= len(todos):
        raise HTTPException(status_code=400, detail="Invalid todo index")
    
    todos[update.index]['done'] = update.done
    job.analysis_todo = todos # Reassign to trigger update
    
    # Force update for JSON types in some SQLalchemys
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(job, "analysis_todo")
    
    db.commit()
    return {"message": "Todo updated"}

class JobContentUpdate(BaseModel):
    semantic_title: Optional[str] = None
    transcription: Optional[str] = None
    analysis_report: Optional[str] = None
    analysis_todo: Optional[list] = None  # Full todo list update

@router.patch("/jobs/{job_id}/content")
async def update_job_content(job_id: str, update: JobContentUpdate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if update.semantic_title is not None:
        job.semantic_title = update.semantic_title
    if update.transcription is not None:
        job.transcription = update.transcription
    if update.analysis_report is not None:
        job.analysis_report = update.analysis_report
    if update.analysis_todo is not None:
        job.analysis_todo = update.analysis_todo
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(job, "analysis_todo")
    
    db.commit()
    db.refresh(job)
    return map_job_to_response(job)

@router.get("/status/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return map_job_to_response(job)

@router.get("/jobs", response_model=List[JobResponse])
async def list_jobs(client_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Job)
    if client_id:
        query = query.filter(Job.client_id == client_id)
    jobs = query.order_by(Job.created_at.desc()).all()
    return [map_job_to_response(job) for job in jobs]

@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}

@router.delete("/jobs")
async def delete_all_jobs(db: Session = Depends(get_db)):
    db.query(Job).delete()
    db.commit()
    return {"message": "All jobs deleted successfully"}

def map_job_to_response(job: Job) -> JobResponse:
    result = None
    if job.status == JobStatus.COMPLETED:
        result = JobResult(
            transcription=job.transcription,
            analysis={
                "report": job.analysis_report,
                "todo_list": job.analysis_todo
            }
        )
    
    return JobResponse(
        job_id=job.id,
        status=job.status,
        filename=job.filename,
        semantic_title=job.semantic_title,
        result=result,
        error=job.error,
        created_at=job.created_at.isoformat(),
        client_name=job.client.name if job.client else None
    )
