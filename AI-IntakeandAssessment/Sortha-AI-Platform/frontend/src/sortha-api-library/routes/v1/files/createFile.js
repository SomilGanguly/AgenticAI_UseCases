const Route = require('../../route')

class CreateFile extends Route {
    constructor(file, fileName, parentFolderID) {
        super();
        this.file = file;
        this.fileName = fileName;
        this.parentFolderID = parentFolderID;
    }
    getMethod() {
        return 'POST';
    }
    getPath() {
        return `/api/files/create_file`;
    }
    needsAuth() {
        return false;
    }
    getBody() {
        const formData = new FormData();
        formData.set('file', this.file);
        formData.set('file_name', this.fileName);
        formData.set('parent_folder_id', this.parentFolderID);
        return formData;
    }
}

module.exports = CreateFile;