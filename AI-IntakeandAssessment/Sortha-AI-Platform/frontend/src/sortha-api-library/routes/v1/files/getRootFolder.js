const Route = require('../../route')

class GetRootFolder extends Route {
    constructor() {
        super();
    }
    getMethod() {
        return 'GET';
    }
    getPath() {
        return `/api/files/root_folders`;
    }
    needsAuth() {
        return false;
    }
    getBody() {
        return null; // No body needed for GET request
    }
}

module.exports = GetRootFolder;