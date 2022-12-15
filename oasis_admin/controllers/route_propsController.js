let All_Models = require('../models/all_models');
/*var Route_Property = require('../models/route_props');
var Route = require('../models/route');*/
let constants = require('../config/constants');
var propnames = {
    'HL7': {
        'outbound_queue': 'Full Queue Name for the consumer to pickup message from',
        'translate_script': 'Python translation script to execute',
        'criteria_script': 'Python wrapper script to execute criteria checking, this usually is a wrapper utilizing the check_criteria script and the criteria properties table',
        'split_script': 'Python wrapper script to execute on a message splitting route'
    },
    'MFT': {
        'mft_script': 'Python script to manipulate and copy the source files to consumers during routing.',
        'key_id': 'PGP option for encryption by key id',
        'encrypt_email': 'PGP option for encryption by email address',
        'passphrase': 'PGP Passphrase'
    }
}

exports.index = function (req, res) {
    All_Models.Route_Property.findAll({
        include: [{
            model: All_Models.Route,
            as: 'Route',
            //where: { producer_id: Sequelize.col('endpoint.id')}
        }]}).then(function (route_props) {
        res.render('route_props', {
            route_props: route_props //send map by guid for output loop
        });
    });
};


exports.get_view = function (req, res) {
    All_Models.Route_Property.findByPk(req.query.id, {
        include: [{
            model: All_Models.Route,
            as: 'Route',
            //where: { producer_id: Sequelize.col('route.id')}
        }]}).then(function (route_prop) {

            if (route_prop.name.includes("password") || route_prop.name.includes("passphrase")){
                route_prop.value = "*****";
            }
            res.render('route_prop_view',  {
                route_prop: route_prop
       }); 
    });
};

exports.get_edit = function (req, res) {
    All_Models.Route_Property.findByPk(req.query.id, {
        include: [{
            model: All_Models.Route,
            as: 'Route',
            //where: { producer_id: Sequelize.col('route.id')}
        }]
    }).then(function (route_prop) {
        res.render('route_prop_edit', {
            route_prop: route_prop,
            env_list: constants.env_list
        });
    });
};

exports.get_create = function (req, res) {
    All_Models.Route.findByPk(req.query.route_id).then(function (route) {
        res.render('route_prop_add', {
            propnames: propnames,
            route: route,
            env_list: constants.env_list
        });
    });
};

exports.post_create = function (req, res) {
    req.body.name = (req.body.name === 'Add New') ? req.body.new_name : req.body.name;
    req.body.name = req.body.name.trim();
    req.body.value = req.body.value.trim();
    All_Models.Route_Property.create(req.body).then(route_prop => {
        res.redirect('/routes/view?id='+route_prop.route_id);
    });
};


exports.post_edit = function (req, res) {
    console.log(req.body);
    All_Models.Route_Property.findByPk(req.body.id, {
        
    }).then(function (route_prop) {
        req.body.name = req.body.name.trim();
        req.body.value = req.body.value.trim();
        route_prop.update(req.body).then(function (route_prop) {
            //lets go back to the Endpoint View that includes props
            //instead of the endpoint props view here
            res.redirect('/routes/view?id='+route_prop.route_id);
        });
    });
};

exports.get_copy = function (req, res) {
    All_Models.Route_Property.findByPk(req.query.id, {
        include: [{
            model: All_Models.Route,
            as: 'Route',
            //where: { producer_id: Sequelize.col('route.id')}
        }]
    }).then(function (route_prop) {
        All_Models.Route.findAll().then(function (routes) {
            res.render('route_prop_copy', {
                route_prop: route_prop,
                routes: routes
            }); 
        });
        
    });
};

exports.post_copy = function (req, res) {
    //console.log(req.body);
    let rarray = req.body.route;
    let rprops = [];
    for(let x = 0;x<rarray.length;x++){
        rprops.push({
            name: req.body.name,
            value: req.body.value,
            env: req.body.env,
            route_id: rarray[x]
        });
    }
    All_Models.Route_Property.bulkCreate(rprops).then(() => {
        res.redirect('/routes');
    });
    
};

exports.get_delete = function (req, res) {
    All_Models.Route_Property.findByPk(req.query.id, {}).then(function (route_prop) {
        //let endpoint_id = endpoint_prop.endpoint_id;
        route_prop.destroy().then(route_prop => {
            res.redirect('/routes/view?id='+route_prop.route_id);
        })
    });
};

