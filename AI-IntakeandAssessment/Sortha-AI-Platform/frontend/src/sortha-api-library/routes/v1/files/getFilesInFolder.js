const Route = require('../../route')

class GetFilesInFolder extends Route {
    constructor(folderID) {
        super();
        this.folderID = folderID;
    }
    getMethod() {
        return 'GET';
    }
    getPath() {
        return `/api/files/files_in_folder/${this.folderID}`;
    }
    needsAuth() {
        return false;
    }
    getBody() {
        return null; // No body needed for GET request
    }
}

module.exports = GetFilesInFolder;