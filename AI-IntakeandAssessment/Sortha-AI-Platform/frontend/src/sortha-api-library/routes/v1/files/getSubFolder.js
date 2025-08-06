const Route = require('../../route')

class GetSubFolder extends Route {
    constructor(folderID) {
        super();
        this.folderID = folderID;
    }
    getMethod() {
        return 'GET';
    }
    getPath() {
        return `/api/files/sub_folders/${this.folderID}`;
    }
    needsAuth() {
        return false;
    }
    getBody() {
        return null; // No body needed for GET request
    }
}

module.exports = GetSubFolder;