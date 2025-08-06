const Route = require('../../route')

class ExecuteWorkflow extends Route {
    constructor(workflowID, workflowBody) {
        super();
        this.workflowID = workflowID;
        this.workflowBody = workflowBody;
    }
    getMethod() {
        return 'POST';
    }
    getPath() {
        return `/api/workflows/execute/${this.workflowID}`;
    }
    needsAuth() {
        return false;
    }
    getBody() {
        return this.workflowBody;
    }
}

module.exports = ExecuteWorkflow;