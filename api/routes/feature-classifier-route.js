module.exports = app => {
    const controller = require('../controller/feature-classifier-controller')();
    app.route('/api/v1/feature/classifier').post(controller.getClassifications);
}