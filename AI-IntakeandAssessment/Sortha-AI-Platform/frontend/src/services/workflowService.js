import GlobalService from '../services/GlobalService';
import GetAllWorkflows from '../sortha-api-library/routes/v1/workflows/getAllWorkflows'

const WorkFlowService = {
    workflows: [],
    hyderateWorkflows: async () => {
        const requestClient = GlobalService.getGlobalData('requestClient');
        const request = requestClient.createRequest(new GetAllWorkflows())
        return request.invoke()
            .then(data => {
                WorkFlowService.workflows = data;
            })
            .catch(error => {
                console.error('Error hydrating workflows:', error);
                throw error;
            });
    },
    getAllWorkflows: async () => {
        if(WorkFlowService.workflows.length === 0) {
            await WorkFlowService.hyderateWorkflows();
        }
        return WorkFlowService.workflows;
    },
    getWorkflowById: async (id) => {
        if (WorkFlowService.workflows[id]) {
            return WorkFlowService.workflows[id];
        } else {
            throw new Error(`Workflow with id ${id} not found`);
        }
    },
    runWorkFlow: async (id, inputs) => {
        if (!WorkFlowService.workflows[id]) {
            throw new Error(`Workflow with id ${id} not found`);
        }
    },
    getWorkflowResults: async (req_id) => {
    }
}

export default WorkFlowService;