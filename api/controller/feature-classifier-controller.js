const {PythonShell} =require('python-shell');

module.exports = () => {
    const controller = {};

    controller.getClassifications = function (req, res) {
        let bodyRes;
        let options = {
            mode: 'json',
            args: JSON.stringify(req.body)
        };

        PythonShell.run('algorithm/classification_algorithm.py', options, function (err, result){
            if (err) throw err;
            res.status(200).send(JSON.parse(result.toString()))
      });

    };

    controller.getHealth = function (req, res) {
        res.status(200).send("feature-classifier UP")
    };

    return controller;
}
