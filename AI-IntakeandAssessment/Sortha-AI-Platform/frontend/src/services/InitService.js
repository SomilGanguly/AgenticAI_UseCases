import GlobalService from './GlobalService';
import Client from '../sortha-api-library/client';
import Authentication from '../sortha-api-library/auth/authentication';

import GlobalConfig from './GlobalConfigService';

const InitService = async () => {
    console.log('Initializing Global Service');
    GlobalService.setGlobalData('requestClient', new Client(GlobalConfig.API_BASE_URL, new Authentication()));
}

export default InitService;