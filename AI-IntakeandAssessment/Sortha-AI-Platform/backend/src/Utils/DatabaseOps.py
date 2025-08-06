from sqlalchemy.orm import Session
from ..Schemas.Folder import Folder
from ..Schemas.File import File

def recusive_delete_folders_and_files(folder_id: int, db: Session):
    # Get all files in the folder
    files = db.query(File).filter(File.parent_folder_id == folder_id).all()
    for file in files:
        db.delete(file)
    
    # Get all subfolders in the folder
    subfolders = db.query(Folder).filter(Folder.parent_folder_id == folder_id).all()
    for subfolder in subfolders:
        recusive_delete_folders_and_files(subfolder.id, db)
    
    # Finally, delete the folder itself
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if folder:
        db.delete(folder)
    
    db.commit()