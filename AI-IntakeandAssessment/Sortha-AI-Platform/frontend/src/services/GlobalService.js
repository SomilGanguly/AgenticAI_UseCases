class GlobalService {
    constructor() {
        if (GlobalService.instance) {
            return GlobalService.instance;
        }
        GlobalService.instance = this;
    }
    getInstance() {
        return GlobalService.instance;
    }
    setGlobalData(key, value) {
        if (!this.globalData) {
            this.globalData = {};
        }
        this.globalData[key] = value;
    }
    getGlobalData(key) {
        if (!this.globalData) {
            return null;
        }
        return this.globalData[key];
    }
}

export default new GlobalService();