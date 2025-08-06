const Route = require('../../route')

class CreateFolder extends Route {
    constructor(name, parentFolderID) {
        super();
        this.name = name;
        this.parentFolderID = parentFolderID;
    }
    getMethod() {
        return 'POST';
    }
    getPath() {
        return `/api/files/create_folder`;
    }
    needsAuth() {
        return false;
    }
    getBody() {
        const js = {
            "name": this.name,
            "parent_folder_id": this.parentFolderID,
        }
        return js;
    }
}

module.exports = CreateFolder;