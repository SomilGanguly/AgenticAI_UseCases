from pydantic import BaseModel, Field
from fastapi import UploadFile
from typing import Union

class CreateFolderRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the folder")
    parent_folder_id: int | None = Field(None, description="ID of the parent folder, if any")
    # owner_team_id: int = Field(..., description="ID of the team that owns the folder")

class CreateFolderResponse(BaseModel):
    id: int = Field(..., description="ID of the created folder")
    name: str = Field(..., min_length=1, max_length=100, description="Name of the folder")
    parent_folder_id: int | None = Field(None, description="ID of the parent folder, if any")
    owner_team_id: int = Field(..., description="ID of the team that owns the folder")

class CreateFileRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the file")
    owner_team_id: int = Field(..., description="ID of the team that owns the file")
    file: UploadFile = Field(..., description="File to be uploaded")

class GenericOperationResponse(BaseModel):
    success: bool = Field(..., description="Indicates whether the folder was successfully deleted")
    message: str = Field(..., description="Message providing additional information about the deletion status")

class FolderView(BaseModel):
    id: int = Field(..., description="ID of the folder")
    name: str = Field(..., min_length=1, max_length=100, description="Name of the folder")
    parent_folder_id: int | None = Field(None, description="ID of the parent folder, if any")
    # owner_team_id: int = Field(..., description="ID of the team that owns the folder")

class FileView(BaseModel):
    id: int = Field(..., description="ID of the file")
    name: str = Field(..., min_length=1, max_length=100, description="Name of the file")
    # owner_team_id: int = Field(..., description="ID of the team that owns the file")
    folder_id: int | None = Field(None, description="ID of the folder containing the file, if any")
    size: int = Field(..., description="Size of the file in bytes")
    