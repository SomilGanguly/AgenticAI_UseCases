const Route = require('../../route')

class GetAllWorkflows extends Route {
    constructor() {
        super();
    }
    getMethod() {
        return 'GET';
    }
    getPath() {
        return `/api/workflows/list`;
    }
    needsAuth() {
        return false;
    }
    getBody() {
        return null; // No body needed for GET request
    }
}

module.exports = GetAllWorkflows;