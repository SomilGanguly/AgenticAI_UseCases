const Route = require('../../route')

class GetStatus extends Route {
    constructor(requestID) {
        super();
        this.requestID = requestID;
    }
    getMethod() {
        return 'GET';
    }
    getPath() {
        return `/api/workflows/get_status/${this.requestID}`;
    }
    needsAuth() {
        return false;
    }
    getBody() {
        return null; // No body needed for GET request
    }
}

module.exports = GetStatus;