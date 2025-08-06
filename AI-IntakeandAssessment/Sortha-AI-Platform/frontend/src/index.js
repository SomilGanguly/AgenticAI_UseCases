import React from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router';
import { useLayoutEffect } from 'react';
// import './index.css';
import App from './App';
import Layout from './layouts/dashboard';

import PipelinesPage from './pages/FileExplorer';
import TemplatesPage from './pages/templates';
import WorkflowPage from './pages/workflow';
import WorkFlowService from './services/workflowService';
import InitService from './services/InitService';


InitService()
.then(async () => {

	// Main Logic
	const getWorkflowRoutes = () => {
		return WorkFlowService.getAllWorkflows()
		.then((workflows) => {
			const arr = [];
			workflows.forEach((workflow) => {
				arr.push({
					path: new String(workflow.id),
					element: <WorkflowPage description={workflow.description} />
				});
			});
			return arr
		})
	}
	
	const router = createBrowserRouter([
		{
			Component: App,
			children: [
				{
					path: '/',
					Component: Layout,
					children: [
						{
							path: 'files',
							Component: PipelinesPage
						},
						{
							path: 'templates',
							Component: TemplatesPage
						},
						{
							path: 'workflow',
							children: await getWorkflowRoutes()
						}
					]
				}
			]
		}
	])
	
	const root = ReactDOM.createRoot(document.getElementById('root'));
	root.render(
		<React.StrictMode>
			<RouterProvider router={router} />
		</React.StrictMode>
	);

});
