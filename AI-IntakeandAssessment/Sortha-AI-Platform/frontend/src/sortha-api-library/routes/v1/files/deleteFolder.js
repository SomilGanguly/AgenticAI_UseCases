const Route = require('../../route')

class DeleteFolder extends Route {
    constructor(folderID) {
        super();
        this.folderID = folderID;
    }
    getMethod() {
        return 'DELETE';
    }
    getPath() {
        return `/api/files/delete_folder/${this.folderID}`;
    }
    needsAuth() {
        return false;
    }
    getBody() {
        return null;
    }
}

module.exports = DeleteFolder;