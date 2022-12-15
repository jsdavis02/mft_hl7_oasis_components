var env = process.env.NODE_ENV || 'development';
var config = require('../config/config')[env];
let All_Models = require('../models/all_models');
//var User = require('../models/user');
const bcrypt = require('bcrypt-nodejs');
const salt = bcrypt.genSaltSync();
//var Endpoint = require('../models/endpoint');
const Sequelize = require('sequelize');
const Op = Sequelize.Op;

exports.index = function (req, res) {
  All_Models.User.findAll({
    include: [{
      model: All_Models.Endpoint,
      attributes: ['id', 'bw_process_ident']
    }],
    order: [['username', 'ASC']]
  }).then(function (users) {
    //console.log(users[0].endpoints[0].bw_process_ident)
    res.render('user', {
      users: users, //send map by guid for output loop
      error_message: req.flash('error_message'),
      success_message: req.flash('success_message'),
    });
  });
};

exports.get_create = function (req, res) {
  All_Models.Endpoint.findAll({
    order: [['bw_process_ident', 'ASC']]
  }).then(function (endpoints) {
    res.render('user_add', {
      endpoints: endpoints,
      endpoints_by_type: All_Models.Endpoint.orderByType(endpoints),
    });
  });

};

exports.post_create = function (req, res) {
  let pass = null;
  if(req.body.password.length > 0){
    pass = bcrypt.hashSync(req.body.password, salt);
  }
  console.log(req.body.password);
  All_Models.User.create({
    username: req.body.username,
    email: req.body.email,
    password: pass,
    role: req.body.role
  }).then(user => {
    let eps = [];
    if(req.body.endpoints !== undefined){
      for(let x=0;x<req.body.endpoints.length;x++){
        eps.push(req.body.endpoints[x])
      }
    }
    user.setEndpoints(eps);
    res.redirect('/users');
  });
};
exports.analyst_get_edit = function (req, res) {
  All_Models.User.findByPk(req.user.id, {
    include: [{model: All_Models.Endpoint}]
  }).then(function (user){
    //make a simple array of endpoint ids for edit page simplicity
    let eids = [];
    for(let i=0;i<user.endpoints.length;i++){ eids.push(user.endpoints[i].id);}
    All_Models.Endpoint.findAll().then(function (endpoints) {
      console.log(eids);
      res.render('analyst_user_edit', {
        user: user,
        endpoints: endpoints,
        eids: eids
      });
    });

  });
};
exports.analyst_post_edit = function (req, res) {
  All_Models.User.findByPk(req.user.id,{
    //include: [{model: Endpoint}]
  }).then(function (user) {
    //console.log(user);
    /*let eps = [];
    if(req.body.endpoints !== undefined){
        for(let x=0;x<req.body.endpoints.length;x++){
            eps.push(req.body.endpoints[x])
        }
    }*/
    user.username = req.body.username;
    user.email = req.body.email;
    //user.role = req.body.role;
    //user.setEndpoints(eps);
    if(req.body.password.length > 0){
      user.password = bcrypt.hashSync(req.body.password, salt);
    }
    user.save().then(()=> {
      res.redirect('/users');
    });
  });

};
exports.get_edit = function (req, res) {
  All_Models.User.findByPk(req.query.id, {
    include: [{model: All_Models.Endpoint}]
  }).then(function (user){
    //make a simple array of endpoint ids for edit page simplicity
    let eids = [];
    for(let i=0;i<user.endpoints.length;i++){ eids.push(user.endpoints[i].id);}
    All_Models.Endpoint.findAll({
      order: [['bw_process_ident', 'ASC']]
    }).then(function (endpoints) {
      //console.log(endpoints_by_type);
      res.render('user_edit', {
        user: user,
        endpoints: endpoints,
        endpoints_by_type: All_Models.Endpoint.orderByType(endpoints),
        eids: eids
      });
    });

  });
};

exports.post_user_endpoint_add = function (req, res) {
  //console.log(req.body);
  All_Models.Endpoint.findByPk(req.body.endpoint_id, {
    include: [{model: All_Models.User}]
  }).then(function (endpoint) {
   
    if (req.body.analyst !== undefined){
      endpoint.setUsers(req.body.analyst);
      //console.log(endpoint);
    } 
    res.redirect('/endpoints/view?id='+req.body.endpoint_id);
  });
  
};

exports.post_edit = function (req, res) {
  All_Models.User.findByPk(req.body.id,{
    include: [{model: All_Models.Endpoint}]
  }).then(function (user) {
    //console.log(user);
    let eps = [];
    if(req.body.endpoints !== undefined){
      for(let x=0;x<req.body.endpoints.length;x++){
        eps.push(req.body.endpoints[x])
      }
    }
    user.username = req.body.username;
    user.email = req.body.email;
    user.role = req.body.role;
    user.setEndpoints(eps);
    if(req.body.password.length > 0){
      user.password = bcrypt.hashSync(req.body.password, salt);
    }
    user.save().then(()=> {
      if(user.role === 'analyst' && env !== 'local'){
        All_Models.Endpoint.findAll({
          where: {
            id: {[Op.in]:eps}
          }
        }).then(function (endpoints) {
          //console.log(endpoints);
          let nodemailer = require('nodemailer');
          var App_Setting = require('../models/app_settings');
          App_Setting.findAll({
            where: {
              env: config.env
            }
          }).then(function (app_settings) {
            let bcc_emails = [];
            for (let setting of app_settings){
              //console.log(setting);
              if(setting.name.includes('notification_email')){ bcc_emails.push(setting.value)}
            }
            let content = 'Your Oasis Analyst User has been updated and is now associated with the below End Points (Data Producers and Consumers).\r\n\r\n';
            content += 'This means you can see data sent or received for all of the below plus view their entire configuration in Oasis.\r\n\r\n';
            for(let endpoint of endpoints){
              content += endpoint.bw_process_ident+' that is a '+endpoint.direction+' with configuration details at: http://'+req.get('host')+'/endpoints/analyst_view?id='+endpoint.id+'\r\n';
            }

            let transporter = nodemailer.createTransport(config.email.smtp);
            transporter.sendMail({
              from: 'oasis@valleywisehealth.org',
              to: user.email,
              bcc: bcc_emails.join(', '),
              replyTo: bcc_emails.join(', '),
              subject: 'User update for Oasis '+config.env,
              text: 'Below is information related to your access to the Oasis Application Integration Platform:\r\n\r\n\r\n'+content,
            }, (err, info) => {
              if(err){
                req.flash('error_message', 'Email failed to send with error: '+err);
              }
              else{
                req.flash('success_message', 'Email sent to: '+user.email);
              }
              res.redirect('/users');
            });
          });
        });

      }
      res.redirect('/users');
    });
  });

};

exports.get_email_invite = function (req, res) {
  All_Models.User.findByPk(req.query.id,{
    include: [{model: All_Models.Endpoint}]
  }).then(function (user) {
    let nodemailer = require('nodemailer');
    var App_Setting = require('../models/app_settings');
    App_Setting.findAll({
      where: {
        env: config.env
      }
    }).then(function (app_settings) {
      let bcc_emails = [];
      for (let setting of app_settings){
        //console.log(setting);
        if(setting.name.includes('notification_email')){ bcc_emails.push(setting.value)}
      }
      let content = 'Please save and bookmark the below url, this is where you can view data moves associated with you and access archives of those transfers.\r\n\r\n';
      content += 'Web Url: http://'+req.get('host')+'\r\n\r\n';
      content += 'Username: '+user.username+'\r\n\r\n';
      content += 'Password: changeme\r\n\r\n';
      content += '** username and password are case sensitive and no spaces **\r\n\r\n';
      content += '!! After login click Account at the top and change your password, this interface gives access to archive data !!\r\n';
      //console.log(answers);
      let transporter = nodemailer.createTransport(config.email.smtp);
      transporter.sendMail({
        from: 'oasis@valleywisehealth.org',
        to: user.email,
        bcc: bcc_emails.join(', '),
        replyTo: bcc_emails.join(', '),
        subject: 'User invitation for Oasis '+config.env,
        text: 'Below is information to access the Oasis Application Integration Platform:\r\n\r\n\r\n'+content,
      }, (err, info) => {
        if(err){
          req.flash('error_message', 'Email failed to send with error: '+err);
        }
        else{
          req.flash('success_message', 'Email sent to: '+user.email);
        }
        res.redirect('/users');
      });
    });
  })};

exports.get_delete = function (req, res) {
  All_Models.User.findByPk(req.query.id, {}).then(function (user) {
    user.destroy().then(() => {
      res.redirect('/users/');
    })
  });
};
