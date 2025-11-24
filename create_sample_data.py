import sys
import os
from datetime import datetime, timedelta
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, Client, Job

def create_sample_data():
    db = SessionLocal()
    
    try:
        # Create clients
        clients = [
            Client(id=str(uuid.uuid4()), name="Acme Corp", created_at=datetime.utcnow() - timedelta(days=30)),
            Client(id=str(uuid.uuid4()), name="TechStart Inc", created_at=datetime.utcnow() - timedelta(days=20)),
            Client(id=str(uuid.uuid4()), name="Global Solutions", created_at=datetime.utcnow() - timedelta(days=10)),
        ]
        
        for client in clients:
            db.add(client)
        db.commit()
        
        print(f"Created {len(clients)} clients")
        
        # Create jobs with different dates
        jobs_data = [
            # Today
            {
                "filename": "morning_standup.mp3",
                "client_id": clients[0].id,
                "created_at": datetime.utcnow() - timedelta(hours=2),
                "status": "completed",
                "transcription": "Today's standup meeting discussing sprint progress and blockers.",
                "analysis_report": "The team discussed current sprint progress. Main focus on completing user authentication feature.",
                "analysis_todo": [
                    {"text": "Complete user authentication module", "done": False},
                    {"text": "Review pull requests from yesterday", "done": True},
                    {"text": "Update documentation for new API endpoints", "done": False}
                ]
            },
            {
                "filename": "client_call_acme.mp3",
                "client_id": clients[0].id,
                "created_at": datetime.utcnow() - timedelta(hours=5),
                "status": "completed",
                "transcription": "Client meeting discussing Q4 requirements and timeline adjustments.",
                "analysis_report": "Client requested additional features for Q4 release. Timeline needs adjustment.",
                "analysis_todo": [
                    {"text": "Prepare revised timeline proposal", "done": False},
                    {"text": "Schedule follow-up meeting for next week", "done": False}
                ]
            },
            # Yesterday
            {
                "filename": "project_planning.mp4",
                "client_id": clients[1].id,
                "created_at": datetime.utcnow() - timedelta(days=1, hours=3),
                "status": "completed",
                "transcription": "Planning session for new mobile app project with TechStart team.",
                "analysis_report": "Discussed architecture decisions for the new mobile application. Team agreed on React Native.",
                "analysis_todo": [
                    {"text": "Set up development environment", "done": True},
                    {"text": "Create initial project structure", "done": True},
                    {"text": "Design database schema", "done": False}
                ]
            },
            {
                "filename": "budget_review.mp3",
                "client_id": clients[2].id,
                "created_at": datetime.utcnow() - timedelta(days=1, hours=8),
                "status": "completed",
                "transcription": "Quarterly budget review meeting with Global Solutions finance team.",
                "analysis_report": "Budget review showed 15% under budget for Q3. Discussed allocation for Q4.",
                "analysis_todo": [
                    {"text": "Prepare Q4 budget proposal", "done": False},
                    {"text": "Review vendor contracts", "done": False}
                ]
            },
            # This week (3 days ago)
            {
                "filename": "design_review.mp4",
                "client_id": clients[1].id,
                "created_at": datetime.utcnow() - timedelta(days=3, hours=2),
                "status": "completed",
                "transcription": "Design review session for TechStart mobile app UI/UX.",
                "analysis_report": "Design team presented mockups. Client requested minor adjustments to color scheme.",
                "analysis_todo": [
                    {"text": "Update color palette in design system", "done": True},
                    {"text": "Create revised mockups", "done": True},
                    {"text": "Send updated designs to client", "done": False}
                ]
            },
            # Last week (5 days ago)
            {
                "filename": "security_audit.mp3",
                "client_id": clients[0].id,
                "created_at": datetime.utcnow() - timedelta(days=5, hours=4),
                "status": "completed",
                "transcription": "Security audit findings discussion for Acme Corp infrastructure.",
                "analysis_report": "Security team identified 3 medium-priority vulnerabilities. Action plan created.",
                "analysis_todo": [
                    {"text": "Patch authentication vulnerability", "done": True},
                    {"text": "Update SSL certificates", "done": True},
                    {"text": "Implement rate limiting", "done": False}
                ]
            },
            # Last week (7 days ago)
            {
                "filename": "kickoff_meeting.mp4",
                "client_id": clients[2].id,
                "created_at": datetime.utcnow() - timedelta(days=7, hours=1),
                "status": "completed",
                "transcription": "Project kickoff meeting with Global Solutions for new CRM system.",
                "analysis_report": "Kickoff meeting established project scope and timeline. Team introductions completed.",
                "analysis_todo": [
                    {"text": "Set up project management tools", "done": True},
                    {"text": "Schedule weekly sync meetings", "done": True},
                    {"text": "Create project charter document", "done": True}
                ]
            },
            # Older (15 days ago)
            {
                "filename": "retrospective.mp3",
                "client_id": clients[1].id,
                "created_at": datetime.utcnow() - timedelta(days=15, hours=3),
                "status": "completed",
                "transcription": "Sprint retrospective discussing what went well and areas for improvement.",
                "analysis_report": "Team identified communication gaps. Agreed to implement daily standups.",
                "analysis_todo": [
                    {"text": "Implement daily standup meetings", "done": True},
                    {"text": "Create team communication guidelines", "done": True}
                ]
            },
            # Processing job
            {
                "filename": "ongoing_discussion.mp3",
                "client_id": clients[0].id,
                "created_at": datetime.utcnow() - timedelta(minutes=5),
                "status": "processing",
            },
            # Queued job
            {
                "filename": "waiting_transcription.mp4",
                "client_id": clients[2].id,
                "created_at": datetime.utcnow() - timedelta(minutes=2),
                "status": "queued",
            }
        ]
        
        for job_data in jobs_data:
            job = Job(
                id=str(uuid.uuid4()),
                filename=job_data["filename"],
                client_id=job_data["client_id"],
                created_at=job_data["created_at"],
                status=job_data["status"],
                language="en",
                model="gpt-4o",
                transcription=job_data.get("transcription"),
                analysis_report=job_data.get("analysis_report"),
                analysis_todo=job_data.get("analysis_todo")
            )
            db.add(job)
        
        db.commit()
        print(f"Created {len(jobs_data)} jobs")
        print("Sample data created successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
