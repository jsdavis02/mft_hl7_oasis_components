var env = process.env.NODE_ENV || 'development';
var config = require('../config/config')[env];
let All_Models = require('../models/all_models');

let constants = require('../config/constants');
const request = require('request-promise');
const moment = require('moment');
const Sequelize = require('sequelize');
const sequelize = new Sequelize(config.database.db,config.database.user,config.database.pass, {
  host: config.database.host,
  dialect: 'mssql',
  operatorsAliases: false,

  pool: {
    max: 5,
    min: 0,
    acquire: 30000,
    idle: 10000
  },
  dialectOptions: {
    useUTC: false
  }

});





exports.get_int_request = function (req, res) {
  //console.log(constants.request_types);
  let contact_email = null;
  console.log(typeof Object.keys(All_Models.Int_Request.rawAttributes));
  console.log(Object.keys(All_Models.Int_Request.rawAttributes));
  res.render('int_request_add', {
    types: constants.endpoint_types,
    route_types: constants.route_types,
    request_types: constants.request_types,
    error_message: req.flash('error_message'),
    success_message: req.flash('success_message'),
    triggerevents: constants.triggerevents,
    contact_email: (req.user && req.user.email)? req.user.email : "",
    
  });
};

exports.post_int_request = function (req, res) {
  All_Models.Int_Request.create(req.body).then(int_request => {
    let int_req_props = [];
    for (const k in req.body){
      if(k !== 'submit' && Object.keys(All_Models.Int_Request.rawAttributes).includes(k) === false && req.body[k].length > 0){
        console.log(k);
        console.log(req.body[k]);
        int_req_props.push(
            {
              int_request_id: int_request.id,
              name: k,
              value: req.body[k],
              env: env
            }
        );
      }
    }
    All_Models.Int_Request_Property.bulkCreate(int_req_props).then(function () {
      req.flash('success_message', 'Integration Request Saved');
      res.redirect('/');  
    });
  });
};

exports.index = function (req, res) {
  All_Models.Int_Request.findAll().then(function (int_requests) {
    res.render('int_request', {
      int_requests: int_requests
    });
  });
};

exports.get_view = function (req, res) {
  All_Models.Int_Request.findByPk(req.query.id, {
    include: [
        {
          model: All_Models.Int_Request_Property,
          as: 'properties',
        }
        ]
  }).then(function (int_request){
    res.render('int_request_view', {
      int_request: int_request
    });
  });
};

exports.get_edit = function (req, res) {
  
};

exports.post_edit = function (req, res) {
  
};

exports.get_delete = function (req, res) {
  
};
