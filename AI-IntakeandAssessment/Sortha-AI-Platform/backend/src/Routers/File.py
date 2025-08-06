from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Response, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from ..Schemas.Folder import Folder
from ..Schemas.File import File
from ..Utils.DatabaseOps import recusive_delete_folders_and_files
from ..Services.FileService.LocalFileService import LocalFileService

from ..Models.File import (
    CreateFolderRequest,
    FolderView,
    FileView,
    GenericOperationResponse
)

router = APIRouter()

# Get Folder by ID
@router.get('/folders/{folder_id}', response_model=FolderView)
def get_folder(folder_id: int, db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="No folders found for this team.")
    return FolderView(id=folder.id, name=folder.name, parent_folder_id=folder.parent_folder_id)

# Create a New folder
@router.post('/create_folder', response_model=FolderView)
def create_folder(req: CreateFolderRequest, db: Session = Depends(get_db)):
    new_folder = Folder(
        name=req.name,
        parent_folder_id=req.parent_folder_id,
        owner_team_id=0
    )
    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)

    return FolderView(
        id=new_folder.id,
        name=new_folder.name,
        parent_folder_id=new_folder.parent_folder_id
    )

# Delete a Folder
@router.delete('/delete_folder/{folder_id}', response_model=GenericOperationResponse)
def delete_folder(folder_id: int, response: Response, db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(
            status_code = 404,
            detail="Folder not found."
        )
    
    # Recursively delete all files and subfolders
    try:
        recusive_delete_folders_and_files(folder_id, db)

        return GenericOperationResponse(
            success=True,
            message="Folder and all its contents deleted successfully."
        )
    except Exception as e:
        return HTTPException(
            status_code = 500,
            detail=f"Error deleting folder: {str(e)}"
        )

# # Get all folders in a team
# @router.get('/folders/team/{team_id}')
# def get_folders_by_team(team_id: int, response: Response, db: Session = Depends(get_db)):
#     folders = db.query(Folder).filter(Folder.owner_team_id == team_id).all()
#     if not folders:
#         response.status_code = 404
#         raise GenericOperationResponse(
#             success=False,
#             message="No folders found for this team."
#         )
#     return folders

# Get all folders in a parent folder
@router.get('/sub_folders/{parent_folder_id}', response_model=list[FolderView] | GenericOperationResponse)
def get_folders_by_parent(parent_folder_id: int, response: Response, db: Session = Depends(get_db)):
    folders = db.query(Folder).filter(Folder.parent_folder_id == parent_folder_id).all()
    if not folders or len(folders) == 0:
        return []
    return [
        FolderView(
            id=folder.id,
            name=folder.name,
            parent_folder_id=folder.parent_folder_id
        ) for folder in folders
    ]

# Get all root folders
@router.get('/root_folders')
def get_root_folders(response: Response, db: Session = Depends(get_db)):
    folders = db.query(Folder).filter(Folder.parent_folder_id.is_(None)).all()
    if not folders:
        return []
    return [
        FolderView(
            id=folder.id,
            name=folder.name,
            parent_folder_id=folder.parent_folder_id
        ) for folder in folders
    ]

# Create a New File
@router.post('/create_file')
def create_file(file: Annotated[UploadFile, FastAPIFile()], file_name: Annotated[str, Form()], parent_folder_id: Annotated[int, Form()], db: Session = Depends(get_db)):
    lfs = LocalFileService.get_instance()
    physical_path = lfs.create_file(file.file, file.filename.split('.')[-1])
    if file_name.split('.')[-1] != file.filename.split('.')[-1]:
        file_name = f"{file_name}.{file.filename.split('.')[-1]}"
    new_file = File(
        name=file_name,
        size=file.size,
        parent_folder_id=parent_folder_id,
        owner_team_id=0,
        file_physcial_address=physical_path,
    )

    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file

# Download a File
@router.get('/download_file/{file_id}')
def download_file(file_id: int, db: Session = Depends(get_db)):
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found.")
    
    lfs = LocalFileService.get_instance()
    
    if lfs.file_exists(file.file_physcial_address) is False:
        raise HTTPException(status_code=404, detail="File not found on server.")
    
    return StreamingResponse(content=lfs.read_file(file.file_physcial_address), media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={file.name}"})

# Delete a File
@router.delete('/delete_file/{file_id}')
def delete_file(file_id: int, response: Response, db: Session = Depends(get_db)):
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        response.status_code = 404
        return GenericOperationResponse(
            success=False,
            message="File not found."
        )
    
    lfs = LocalFileService.get_instance()
    try:
        lfs.delete_file(file.file_physcial_address)
        db.delete(file)
        db.commit()
        
        return GenericOperationResponse(
            success=True,
            message="File deleted successfully."
        )
    except FileNotFoundError as e:
        response.status_code = 404
        return GenericOperationResponse(
            success=False,
            message=str(e)
        )
    except Exception as e:
        response.status_code = 500
        return GenericOperationResponse(
            success=False,
            message=f"Error deleting file: {str(e)}"
        )

# Get all files in folder
@router.get('/files_in_folder/{folder_id}')
def get_files_in_folder(folder_id: int, response: Response, db: Session = Depends(get_db)):
    files = db.query(File).filter(File.parent_folder_id == folder_id).all()
    if not files:
        return []
    return [
        FileView(
            id=file.id,
            name=file.name,
            folder_id=file.parent_folder_id,
            size=file.size
        ) for file in files
    ]

# Root level cannot have files, only folders
# # Get all files at root level
# @router.get('/root_files')
# def get_root_files(response: Response, db: Session = Depends(get_db)):
#     files = db.query(File).filter(File.parent_folder_id.is_(None)).all()
#     if not files:
#         response.status_code = 404
#         return HTTPException(
#             status_code=404,
#             detail="No root files found."
#         )
#     return [
#         FileView(
#             id=file.id,
#             name=file.name,
#             folder_id=file.parent_folder_id,
#             size=file.size
#         ) for file in files
#     ]