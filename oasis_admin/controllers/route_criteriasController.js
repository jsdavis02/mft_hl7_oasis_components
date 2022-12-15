let All_Models = require('../models/all_models');
var Route_Criteria = require('../models/route_criterias');
var Route = require('../models/route');
//var Endpoint = require('../models/endpoint');


exports.index = function (req, res) {
    All_Models.Route_Criteria.findAll({
        include: [{
            model: All_Models.Route,
            as: 'Route',
            //where: { producer_id: Sequelize.col('endpoint.id')}
        }]}).then(function (route_criterias) {
        res.render('route_criterias', {
            route_criterias: route_criterias //send map by guid for output loop
        });
    });
};


exports.get_view = function (req, res) {
    All_Models.Route_Criteria.findByPk(req.query.id, {
        include: [{
            model: All_Models.Route,
            as: 'Route',
            //where: { producer_id: Sequelize.col('route.id')}
        }]}).then(function (route_criteria) {
       res.render('route_criteria_view',  {
           route_criteria: route_criteria
       }); 
    });
};

exports.get_edit = function (req, res) {
    All_Models.Route_Criteria.findByPk(req.query.id, {
        include: [{
            model: All_Models.Route,
            as: 'Route',
            //where: { producer_id: Sequelize.col('route.id')}
        }]
    }).then(function (route_criteria) {
        res.render('route_criteria_edit', {
            route_criteria: route_criteria
        });
    });
};

exports.post_edit = function (req, res) {
    All_Models.Route_Criteria.findByPk(req.body.id, {
        include: [{
            model: All_Models.Route,
            as: 'Route',
            //where: { producer_id: Sequelize.col('route.id')}
        }]
    }).then(function (route_criteria) {
        //console.log(route_criteria);
        route_criteria.update(req.body).then(function (route_criteria) {
            res.redirect('/routes/view?id='+route_criteria.route_id);
        })
    });
};

exports.get_create = function (req, res) {
    All_Models.Route.findByPk(req.query.route_id).then(function (route) {
        res.render('route_criteria_add', {
            route: route
        });
    });
};

exports.post_create = function (req, res) {
    All_Models.Route_Criteria.create(req.body).then(route_criteria => {
        console.log(route_criteria.route_id);
        res.redirect('/routes/view?id='+route_criteria.route_id);
    });
};

exports.get_delete = function (req, res) {
    All_Models.Route_Criteria.findByPk(req.query.id, {}).then(function (route_criteria) {
        route_criteria.destroy().then(route_criteria => {
        res.redirect('/routes/view?id='+route_criteria.route_id);
        })
    });
};
