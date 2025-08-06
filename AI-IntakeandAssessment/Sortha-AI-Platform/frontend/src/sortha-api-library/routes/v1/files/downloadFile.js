const Route = require('../../route')

class DownloadFile extends Route {
    constructor(fileID) {
        super();
        this.fileID = fileID;
    }
    getMethod() {
        return 'GET';
    }
    getPath() {
        return `/api/files/download_file/${this.fileID}`;
    }
    needsAuth() {
        return false;
    }
    getBody() {
        return null; // No body needed for GET request
    }
}

module.exports = DownloadFile;