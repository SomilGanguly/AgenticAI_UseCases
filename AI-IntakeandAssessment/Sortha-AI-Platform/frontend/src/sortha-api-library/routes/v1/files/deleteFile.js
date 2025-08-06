const Route = require('../../route')

class DeleteFile extends Route {
    constructor(fileID) {
        super();
        this.fileID = fileID;
    }
    getMethod() {
        return 'DELETE';
    }
    getPath() {
        return `/api/files/delete_file/${this.fileID}`;
    }
    needsAuth() {
        return false;
    }
    getBody() {
        return null;
    }
}

module.exports = DeleteFile;