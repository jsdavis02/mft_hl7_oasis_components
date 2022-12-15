let All_Models = require('../models/all_models');

let constants = require('../config/constants');
var propnames = constants.endpoint_propnames;
const env = process.env.NODE_ENV || 'development';
const config = require('../config/config')[env];
const nacl = require('tweetnacl');
const utils = require('tweetnacl-util');
const encodeBase64 = utils.encodeBase64;
const decodeBase64 = utils.decodeBase64;
const encodeUTF8 = utils.encodeUTF8;
const nonce = nacl.randomBytes(24);
const secretKey = config.encryption.secret;

exports.index = function (req, res) {
    All_Models.Endpoint_Property.findAll({
        include: [{
            model: All_Models.Endpoint,
            as: 'Endpoint',
            //where: { producer_id: Sequelize.col('endpoint.id')}
        }]}).then(function (endpoint_props) {
        res.render('endpoint_props', {
            endpoint_props: endpoint_props //send map by guid for output loop
        });
    });
};

exports.get_view = function (req, res) {
    All_Models.Endpoint_Property.findByPk(req.query.id, {
        include: [{
            model: All_Models.Endpoint,
            as: 'Endpoint',
            //where: { producer_id: Sequelize.col('endpoint.id')}
        }]
    }).then(function (endpoint_prop) {

        if (endpoint_prop.name.includes("password") || endpoint_prop.name.includes("passphrase")) {
            endpoint_prop.value = "*****";
        }
        res.render('endpoint_prop_view', {
            endpoint_prop: endpoint_prop
        });
    })
};

exports.get_view_decrypted = function (req, res) {
    All_Models.Endpoint_Property.findByPk(req.query.id, {
        include: [{
            model: All_Models.Endpoint,
            as: 'Endpoint',
            //where: { producer_id: Sequelize.col('endpoint.id')}
        }]
    }).then(function (endpoint_prop) {

        if (endpoint_prop.name.includes("password") || endpoint_prop.name.includes("passphrase")) {
            let v = endpoint_prop.value.split(':');
            let nonce = decodeBase64(v[0]);
            let p = decodeBase64(v[1]);
            endpoint_prop.value = encodeUTF8(nacl.secretbox.open(p, nonce, secretKey));
        }
        res.render('endpoint_prop_view', {
            endpoint_prop: endpoint_prop
        });
    })
};

exports.get_edit = function (req, res) {
    All_Models.Endpoint_Property.findByPk(req.query.id, {
        include: [{
            model: All_Models.Endpoint,
            as: 'Endpoint',
            //where: { producer_id: Sequelize.col('endpoint.id')}
        }]
    }).then(function (endpoint_prop) {
        
        res.render('endpoint_prop_edit', {
            endpoint_prop: endpoint_prop,
            env_list: constants.env_list
        });
    });
};

exports.post_edit = function (req, res) {
    console.log(req.body);
    All_Models.Endpoint_Property.findByPk(req.body.id, {
        include: [{
            model: All_Models.Endpoint,
            as: 'Endpoint',
            //where: { producer_id: Sequelize.col('endpoint.id')}
        }]
    }).then(function (endpoint_prop) {
        if(req.body.name.includes('password') || req.body.name.includes('passphrase')) {
            if(req.body.value !== req.body.orig_val){
                //lets encrypt the value here
                const secretData = Buffer.from(req.body.value, 'utf8');
                const encrypted = nacl.secretbox(secretData, nonce, secretKey);
                const result = `${encodeBase64(nonce)}:${encodeBase64(encrypted)}`;
                req.body.value = result;
            }
            
        }
        req.body.name = req.body.name.trim();
        req.body.value = req.body.value.trim();
        endpoint_prop.update(req.body).then(function (endpoint_prop) {
            //lets go back to the Endpoint View that includes props
            //instead of the endpoint props view here
            res.redirect('/endpoints/view?id='+endpoint_prop.endpoint_id);
        });
    });
};

exports.get_create = function (req, res) {
    All_Models.Endpoint.findByPk(req.query.endpoint_id).then(function (endpoint) {
        res.render('endpoint_prop_add', {
            propnames: propnames,
            endpoint: endpoint,
            env_list: constants.env_list
        });
    });
};

exports.post_create = function (req, res) {
    req.body.name = (req.body.name === 'Add New') ? req.body.new_name : req.body.name;
    if(req.body.name.includes('password') || req.body.name.includes('passphrase')) {
        //lets encrypt the value here
        const secretData = Buffer.from(req.body.value, 'utf8');
        const encrypted = nacl.secretbox(secretData, nonce, secretKey);
        const result = `${encodeBase64(nonce)}:${encodeBase64(encrypted)}`;
        req.body.value = result;
    }
    req.body.name = req.body.name.trim();
    req.body.value = req.body.value.trim();
    All_Models.Endpoint_Property.create(req.body).then(endpoint_prop => {
        res.redirect('/endpoints/view?id='+endpoint_prop.endpoint_id);
    });
};

exports.get_delete = function (req, res) {
    All_Models.Endpoint_Property.findByPk(req.query.id, {}).then(function (endpoint_prop) {
        //let endpoint_id = endpoint_prop.endpoint_id;
        endpoint_prop.destroy().then(endpoint_prop => {
            res.redirect('/endpoints/view?id='+endpoint_prop.endpoint_id);
        })
    });
};
