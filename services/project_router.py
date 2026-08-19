from typing import List
from fastapi import APIRouter, status, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from schema.project import ProjectSchema, VisibilitySchema
from schema.user import PasswordSchema
import services.controller as controller
from services.db import get_db
from services.models import UserModel
from services.storage_service import upload_image_to_imagekit

# All routes in this router will be prefixed with /projects
router = APIRouter(prefix="/projects", tags=["projects"])


# Create a project for a user -> POST /projects/create_project/for_user/{user_id}
@router.post("/create_project/for_user/{user_id}", status_code=status.HTTP_201_CREATED, response_model=ProjectSchema)
def create_project_endpoint(user_id: int, project: ProjectSchema, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return controller.create_project(user_id, project, db)


# List all projects for a user -> GET /projects/list_projects/for_user/{user_id}
@router.get("/list_projects/for_user/{user_id}", status_code=status.HTTP_200_OK, response_model=List[ProjectSchema])
def get_projects_endpoint(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    projects = controller.get_projects(user_id, db)
    return [ProjectSchema.model_validate(p) for p in projects]



# Delete a project -> DELETE /projects/delete_project/{project_id}
@router.delete("/delete_project/{project_id}", status_code=status.HTTP_200_OK)
def delete_project_endpoint(project_id: int, body: PasswordSchema, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
    return controller.delete_project(project_id, body.password, current_user.id, db)


# Update a project -> PUT /projects/update_project/{project_id}
@router.put("/update_project/{project_id}", status_code=status.HTTP_200_OK, response_model=ProjectSchema)
def update_project_endpoint(project_id: int, project: ProjectSchema, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
    return controller.update_project(project_id, project, current_user.id, db)


# Get project visibility -> GET /projects/get_visibility/{project_id}
@router.get("/get_visibility/{project_id}", status_code=status.HTTP_200_OK)
def get_visibility_endpoint(project_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
    return controller.get_project_visibility(project_id, current_user.id, db)


# Update project visibility -> PUT /projects/update_visibility/{project_id}
@router.put("/update_visibility/{project_id}", status_code=status.HTTP_200_OK)
def update_visibility_endpoint(project_id: int, body: VisibilitySchema, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
    return controller.update_project_visibility(project_id, body.visibility, current_user.id, db)


# Upload project image -> POST /projects/{project_id}/upload_image
@router.post("/{project_id}/upload_image", status_code=status.HTTP_200_OK, response_model=ProjectSchema)
async def upload_project_image_endpoint(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(controller.is_authenticated)
):
    try:
        # 1. Read file content
        content = await file.read()

        # 2. Upload to ImageKit
        public_url = upload_image_to_imagekit(content, file.filename)

        # 3. Update project in database
        updated_project = controller.update_project_image_url(project_id, public_url, current_user.id, db)

        # Explicitly validate against schema to catch serialization errors early
        return ProjectSchema.model_validate(updated_project)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# List all public projects for Community Gallery -> GET /projects/public
@router.get("/public", status_code=status.HTTP_200_OK)
def get_public_projects_endpoint(skip: int = 0, limit: int = 10, search: str = None, db: Session = Depends(get_db)):
    return controller.get_public_projects(db, skip=skip, limit=limit, search=search)


