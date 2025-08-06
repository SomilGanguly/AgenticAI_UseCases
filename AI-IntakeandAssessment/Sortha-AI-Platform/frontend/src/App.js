import AreaChartIcon from '@mui/icons-material/AreaChart';
import SettingsIcon from '@mui/icons-material/Settings';
import { ReactRouterAppProvider } from '@toolpad/core/react-router'
import { Outlet } from 'react-router';
import logo from './assets/img/logo.PNG';
import WorkFlowService from './services/workflowService';
import { useLayoutEffect, useState } from 'react';

const App = (props) => {
	const [workflowNav, setWorkflowNav] = useState([{
			segment: 'files',
			title: 'Files',
			icon: <AreaChartIcon />,
		},
		{
			kind: 'header',
			title: 'Workflows'
		}]);
	
	useLayoutEffect(() => {
		loadWorkflows();
	}, []);

	const loadWorkflows = () => {
		WorkFlowService.getAllWorkflows()
		.then((workflows) => {
			workflows.forEach((workflow) => {
				setWorkflowNav([...workflowNav, {
					segment: `workflow/${new String(workflow.id)}`,
					title: workflow.name,
					icon: <SettingsIcon />,
				}]);
			});
		})
	}
	
	const branding = {
		title: 'Sortha',
		logo: <img src={logo} alt="MUI logo" />,
	}

	return (
		<ReactRouterAppProvider
			navigation={workflowNav}
			branding={branding}
		>
			<Outlet />
		</ReactRouterAppProvider>
	);
}

export default App
