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

exports.post_duplicate = function(req, res) {
  const Op = Sequelize.Op;
  console.log(req.body);
  //save new endpoint
  req.body.active = (req.body.active === 'on') ? 1 : 0;
  All_Models.Endpoint.create(req.body).then(endpoint => {
    //lets create endpoint properties selected
    var pids = [];
    var sids = [];
    for (let e_form_key in req.body) {
      if(e_form_key.startsWith('prop_')){
        pids.push(e_form_key.split('_')[1]);
      }
      if(e_form_key.startsWith('schedule_')){
        sids.push(e_form_key.split('_')[1]);
      }
    }
    let ep_where = {
      id: { [Op.in]: pids }
    };
    let es_where = {
      id: { [Op.in]: sids }
    };
    All_Models.Endpoint_Property.findAll({where: ep_where}).then(function (endpoint_props) {
      //copy the props with new endpoint id
      let newprops = [];
      for(let x = 0; x < endpoint_props.length; x++){
        newprops.push({
          endpoint_id: endpoint.id,
          name: endpoint_props[x].name,
          value: endpoint_props[x].value,
          env: endpoint_props[x].env
        });
      }
      All_Models.MFT_Schedule.findAll({where: es_where}).then(function (mft_schedules) {
        let newschedules = [];
        for(let x = 0; x < mft_schedules.length; x++){
          newschedules.push({
            endpoint_id: endpoint.id,
            name: mft_schedules[x].name,
            active: mft_schedules[x].active,
            freq_type: mft_schedules[x].freq_type,
            freq_interval: mft_schedules[x].freq_interval,
            spec_date: mft_schedules[x].spec_date,
            spec_time: mft_schedules[x].spec_time,
          });
        }
        All_Models.Endpoint_Property.bulkCreate(newprops).then(()=> {
          All_Models.MFT_Schedule.bulkCreate(newschedules).then(()=> {
            res.redirect('/endpoints/view?id='+endpoint.id);
          });  
        });
      });
    });
    
  });
  
};

exports.get_duplicate = function(req, res) {
  All_Models.Endpoint.findByPk(req.query.id, {
  }).then(function (endpoint) {
    //get the endpoint props too
    All_Models.Endpoint_Property.findAll({where: {endpoint_id: req.query.id}}).then(function (endpoint_props) {
      for (let i = 0; i < endpoint_props.length; i++) {
        if (endpoint_props[i].name.includes("password")) {
          endpoint_props[i].value = "*****";
        }
      }
      All_Models.MFT_Schedule.findAll({where: {endpoint_id: req.query.id}}).then(function (mft_schedules) {
        res.render('endpoint_dupe_view', {
          types: constants.endpoint_types,
          endpoint: endpoint,
          endpoint_props: endpoint_props,
          mft_schedules: mft_schedules,
          dateformat: require('dateformat')
        });
      });
    });
  });
};

exports.analyst_get_app_restart = function (req, res) {
  All_Models.User.findByPk(req.user.id,{
    include: [{model: All_Models.Endpoint}]
  }).then(function (user) {
    var eids = [];
    for (let e = 0; e < user.endpoints.length; e++) {
      eids.push(user.endpoints[e].id);
    }
    if (!eids.includes(req.query.id)) {
      //analyst is not assigned to this endpoint
      return res.redirect('/endpoints/analyst');

    }
    All_Models.Endpoint.findByPk(req.query.id, {}).then(function (endpoint) {
      const req_options = {
        method: 'GET',
        uri: 'http://' + config.bw.host + ':' + config.bw.ops_port + '/bwappstart?appspace=Oasis-HL7&domain=OASIS&bw_ident=' + endpoint.bw_process_ident,
        json: true,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      };

      request(req_options).then(function (bwresponse) {
        res.redirect('/endpoints/analyst_view?id=' + endpoint.id);
      });
    });
  });
};

exports.get_app_restart = function (req, res) {
  All_Models.Endpoint.findByPk(req.query.id, {
  }).then(function (endpoint) {
    const req_options = {
      method: 'GET',
      uri: 'http://'+config.bw.host+':'+config.bw.ops_port+'/bwappstart?appspace=Oasis-HL7&domain=OASIS&bw_ident='+endpoint.bw_process_ident,
      json: true,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };

    request(req_options).then(function (bwresponse) {
      res.redirect('/endpoints/view?id='+endpoint.id);
    });
  });
};

exports.analyst = function (req, res) {
  All_Models.User.findByPk(req.user.id,{
    include: [{model: All_Models.Endpoint}]
  }).then(function (user) {
    const Op = Sequelize.Op;
    var eids = [];
    for (let e = 0; e < user.endpoints.length; e++) {
      eids.push(user.endpoints[e].id);
    }
    var where = {};
    var apfilters = {
      'active': '',
      'direction': '',
      'type': ''
    };
    var qdata = [];
    //var fs = require('fs');
    var lineReader = require('readline').createInterface({
      input: require('fs').createReadStream(config.bw.queuelist)
    });

    //analyst view only can see their endpoints
    if(req.user.role === 'admin'){
      where = {};
    }
    else {
      where = {id: {[Op.in]: eids}};
    }
    for (const qk in req.query) {
      for (const key in All_Models.Endpoint.rawAttributes) {
        if (qk === key) {
          where[key] = req.query[qk];
        } else {
          //here we put all the parms that are not this key as a string to append
          // to each url filter so we can do combinations so
          // apfilters['active'] = direction=producer&type=HL7
          //console.log(apfilters[key]);
          if (apfilters.hasOwnProperty(key) && apfilters[key].length > 0) {
            apfilters[key] = apfilters[key] + '&' + qk + '=' + req.query[qk];
          } else {
            apfilters[key] = qk + '=' + req.query[qk];
          }
        }
      }
    }

    //console.log(apfilters);
    lineReader.on('line', function (line) {
      console.log('Line from file:', line);
      if (line.includes('oasis') && !line.includes('Command:')) {
        lsplit = line.split(/\s+/);
        qdata.push({
          queue_name: lsplit[0] + ' ' + lsplit[1],
          prefetch_count: lsplit[3],
          consumers: lsplit[4],
          pending: lsplit[5],
          pending_size: lsplit[6] + ' ' + lsplit[7],
          persistent: lsplit[8],
          persistent_size: lsplit[9] + ' ' + lsplit[10]

        });
      }

    });

    All_Models.Endpoint.findAll({
      where: where,
      order: [['id', 'DESC']]
    }).then(function (endpoints) {
      /*const req_options = {
        method: 'GET',
        uri: 'http://' + config.bw.host + ':' + config.bw.ops_port + '/bwapps?appspace=Oasis-HL7&domain=OASIS',
        json: true,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      };

      request(req_options).then(function (bwresponse) {
        for (let i = 0; i < endpoints.length; i++) {
          endpoints[i].run_status = {status: ""};
          for (let x = 0; x < bwresponse.length; x++) {
            if (bwresponse[x].endpoint.startsWith(endpoints[i].bw_process_ident)) {
              endpoints[i].run_status = bwresponse[x];
            }
          }
        }*/
        console.log(constants.endpoint_types);
        res.render('endpoint_analyst', {
          endpoints: endpoints, //send map by guid for output loop
          qdata: qdata,
          wparms: where,
          appendfilters: apfilters,
          endpoint_types: constants.endpoint_types,
          error_message: req.flash('error_message'),
          success_message: req.flash('success_message'),
          //endpoint_status: bwresponse
        });
      //});
    });
  });
};
exports.analyst_post_search = function (req, res) {
  
  const Op = Sequelize.Op;
  All_Models.User.findByPk(req.user.id,{
    include: [{model: All_Models.Endpoint}]
  }).then(function (user) {
    const Op = Sequelize.Op;
    var eids = [];
    for (let e = 0; e < user.endpoints.length; e++) {
      eids.push(user.endpoints[e].id);
    }
    let e_prop_where = {
      [Op.and]: [
        {endpoint_id: {[Op.in]: eids}},
        {[Op.or]: [
          {
            name: {[Op.like]: '%' + req.body.search + '%'}
          },
          {
            value: {[Op.like]: '%' + req.body.search + '%'}
          }
        ]}
      ]
    };


    All_Models.Endpoint_Property.findAll({where: e_prop_where}).then(function (endpoint_props) {
      var consolidated = {};
      var eid = [];
      for (let x = 0; x < endpoint_props.length; x++) {
        eid.push(endpoint_props[x].endpoint_id);
        if (consolidated[endpoint_props[x].endpoint_id] !== undefined && consolidated[endpoint_props[x].endpoint_id].hasOwnProperty('properties')) {
          consolidated[endpoint_props[x].endpoint_id]['properties'].push(endpoint_props[x]);
        } else {
          consolidated[endpoint_props[x].endpoint_id] = {'properties': [endpoint_props[x]]};
        }
      }

      let e_where = {
        [Op.and]: [
          {id: {[Op.in]: eids}},
          {[Op.or]: [
            {
              organization: {[Op.like]: '%' + req.body.search + '%'}
            },
            {
              software: {[Op.like]: '%' + req.body.search + '%'}
            },
            {
              doclink: {[Op.like]: '%' + req.body.search + '%'}
            },
            {
              subsystem: {[Op.like]: '%' + req.body.search + '%'}
            },
            {
              description: {[Op.like]: '%' + req.body.search + '%'}
            },
            {
              bw_process_ident: {[Op.like]: '%' + req.body.search + '%'}
            },
            {
              receiving_app: {[Op.like]: '%' + req.body.search + '%'}
            },
            {
              receiving_facility: {[Op.like]: '%' + req.body.search + '%'}
            },
            {
              name: {[Op.like]: '%' + req.body.search + '%'}
            },
            {
              id: {[Op.in]: eid}
            }
          ]}
        ]
      };
      All_Models.Endpoint.findAll({where: e_where}).then(function (endpoints) {
        for (let i = 0; i < endpoints.length; i++) {
          if (consolidated[endpoints[i].id] === undefined) {
            consolidated[endpoints[i].id] = {'endpoint': endpoints[i]};
          } else {
            consolidated[endpoints[i].id].endpoint = endpoints[i];
          }

        }
        /*if(consolidated[endpoint_props[x].endpoint_id]['endpoint'] === undefined){
          All_Models.Endpoint.findByPk(endpoint_props[x].endpoint_id, {
          }).then(function (endpoint) {
            consolidated[endpoint_props[x].endpoint_id] = {'endpoint': endpoint};
          });
        }
      */
        //console.log(consolidated);
        res.render('endpoint_analyst_search', {
          endpoints: consolidated
        });
      });
    });
  });
};

exports.index = function (req, res) {
  var where = {};
  var apfilters = {
    'active': '',
    'direction': '',
    'type': ''
  };
  var qdata = [];
  //var fs = require('fs');
  var lineReader = require('readline').createInterface({
    input: require('fs').createReadStream(config.bw.queuelist)
  });


  for (const qk in req.query){
    for (const key in All_Models.Endpoint.rawAttributes) {
      if (qk === key) {
        where[key] = req.query[qk];
      }
      else {
        //here we put all the parms that are not this key as a string to append
        // to each url filter so we can do combinations so
        // apfilters['active'] = direction=producer&type=HL7
        //console.log(apfilters[key]);
        if(apfilters.hasOwnProperty(key) && apfilters[key].length > 0){
          apfilters[key] = apfilters[key]+'&'+qk+'='+req.query[qk];
        }
        else{
          apfilters[key] = qk+'='+req.query[qk];
        }
      }
    }
  }
  //console.log(apfilters);
  lineReader.on('line', function (line) {
    console.log('Line from file:', line);
    if(line.includes('oasis') && !line.includes('Command:')){
      lsplit = line.split(/\s+/);
      qdata.push({
        queue_name: lsplit[0]+' '+lsplit[1],
        prefetch_count: lsplit[3],
        consumers: lsplit[4],
        pending: lsplit[5],
        pending_size: lsplit[6]+' '+lsplit[7],
        persistent: lsplit[8],
        persistent_size: lsplit[9]+' '+lsplit[10]

      });
    }

  });

  All_Models.Endpoint.findAll({
    where: where,
    order: [['id','DESC']]
  }).then(function (endpoints) {
    /*const req_options = {
      method: 'GET',
      uri: 'http://'+config.bw.host+':'+config.bw.ops_port+'/bwapps?appspace=Oasis-HL7&domain=OASIS',
      json: true,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };

    request(req_options).then(function (bwresponse) {
      for(let i = 0;i<endpoints.length; i++){
        endpoints[i].run_status = {status: ""};
        for(let x = 0;x<bwresponse.length;x++){
          if(bwresponse[x].endpoint.startsWith(endpoints[i].bw_process_ident)){
            endpoints[i].run_status = bwresponse[x];
          }
        }
      }*/
      res.render('endpoint', {
        endpoints: endpoints, //send map by guid for output loop
        qdata: qdata,
        wparms: where,
        appendfilters: apfilters,
        endpoint_types: constants.endpoint_types,
        error_message: req.flash('error_message'),
        success_message: req.flash('success_message'),
        //endpoint_status: bwresponse
      });
    });
  //});
};

exports.get_mft_request = function (req, res) {
  res.render('mft_request', {
    types: constants.endpoint_types,
    error_message: req.flash('error_message'),
    success_message: req.flash('success_message'),
  });
};

exports.post_mft_request = function (req, res) {
  let nodemailer = require('nodemailer');
  var App_Setting = require('../models/app_settings');
    App_Setting.findAll({
      where: {
        env: config.env
      }
    }).then(function (app_settings) {
      let to_emails = [];
      for (let setting of app_settings){
        //console.log(setting);
        if(setting.name.includes('notification_email')){ to_emails.push(setting.value)}
      }
      let answers = '';
      for (let f in req.body){
        answers += f+': '+req.body[f]+'\r\n';
      }
      //console.log(answers);
      let transporter = nodemailer.createTransport(config.email.smtp);
      transporter.sendMail({
        from: 'oasis@valleywisehealth.org',
        to: to_emails.join(', '),
        subject: 'New MFT Request for Oasis',
        text: 'Below is a new MFT request:\r\n'+answers,
      }, (err, info) => {
        if(err){
          req.flash('error_message', 'Email failed to send with error: '+err);
        }
        else{
          req.flash('success_message', 'Email sent to: '+to_emails.join(', '));
        }
        res.redirect('/endpoints/mft_request');
      });
  });
};

exports.get_create = function (req, res) {
  res.render('endpoint_add', {
    types: constants.endpoint_types,
    //TODO sync form/views to display values from constants that match alert email labels
    alert_levels: constants.alert_levels,
  });
};

exports.post_create = function (req, res) {
  req.body.active = (req.body.active === 'on') ? 1 : 0;
  All_Models.Endpoint.create(req.body).then(endpoint => { res.redirect('/endpoints/view?id='+endpoint.id)});
};

exports.get_view = function (req, res) {
  All_Models.Endpoint.findByPk(req.query.id, {
    include: [{model: All_Models.User}]
  }).then(function (endpoint) {
    console.log(endpoint.users);
    var routewhere = {where: {producer_id: req.query.id}};
    if(endpoint.direction === 'consumer'){
      routewhere = {where: {consumer_id: req.query.id}};
    }
    All_Models.Endpoint_Property.findAll(
        {
          where: {endpoint_id: req.query.id},
          order: [['env', 'ASC'],['name', 'ASC'] ]
        }
        ).then(function (endpoint_props) {
      for(let i=0; i < endpoint_props.length; i++) {
          if (endpoint_props[i].name.includes("password") || endpoint_props[i].name.includes("passphrase")){
          endpoint_props[i].value = "*****";
        }
      }
      All_Models.Route.findAll(routewhere).then(function (routes) {
        All_Models.MFT_Schedule.findAll({where: {endpoint_id: req.query.id}}).then(function (mft_schedules) {
          All_Models.User.findAll({
            where: {
              "role": "analyst"
            },
            order: [['email', 'ASC']]
          }).then(function (analysts) {
           
            for (let m=0; m < mft_schedules.length; m++){
              mft_schedules[m] = mft_schedules[m].setValuesForDisplay();
            }
            let uids = [];
            for(let i=0;i<endpoint.users.length;i++){ uids.push(endpoint.users[i].id);}
            res.render('endpoint_view', {
              endpoint: endpoint,
              routes: routes,
              endpoint_props: endpoint_props,
              mft_schedules: mft_schedules,
              dateformat: require('dateformat'),
              moment: moment,
              error_message: req.flash('error_message'),
              success_message: req.flash('success_message'),
              //TODO sync form/views to display values from constants that match alert email labels
              alert_levels: constants.alert_levels,
              analysts: analysts,
              uids: uids,
            });
          });
          //});
        });

      });
    });

  });

};

exports.analyst_get_view = function (req, res) {
  All_Models.User.findByPk(req.user.id,{
    include: [{model: All_Models.Endpoint}]
  }).then(function (user) {
    var eids = [];
    for (let e = 0; e < user.endpoints.length; e++) {
      eids.push(user.endpoints[e].id);
    }
    if(!eids.includes(req.query.id) && user.role !== 'admin'){
      //analyst is not assigned to this endpoint
      return res.redirect('/endpoints/analyst');
      
    }
    All_Models.Endpoint.findByPk(req.query.id, {}).then(function (endpoint) {
      var routewhere = {where: {producer_id: req.query.id}};
      if (endpoint.direction === 'consumer') {
        routewhere = {where: {consumer_id: req.query.id}};
      }
      All_Models.Endpoint_Property.findAll({where: {endpoint_id: req.query.id}}).then(function (endpoint_props) {
        for (let i = 0; i < endpoint_props.length; i++) {
          if (endpoint_props[i].name.includes("password")) {
            endpoint_props[i].value = "*****";
          }
        }
        All_Models.Route.findAll(routewhere).then(function (routes) {
          All_Models.MFT_Schedule.findAll({where: {endpoint_id: req.query.id}}).then(function (mft_schedules) {
            /*const req_options = {
              method: 'GET',
              uri: 'http://' + config.bw.host + ':' + config.bw.ops_port + '/bwapps?appspace=Oasis-HL7&domain=OASIS',
              json: true,
              headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
              }
            };

            request(req_options).then(function (bwresponse) {

              endpoint.run_status = {status: ""};
              for (let x = 0; x < bwresponse.length; x++) {
                if (bwresponse[x].endpoint.startsWith(endpoint.bw_process_ident)) {
                  endpoint.run_status = bwresponse[x];
                }
              }*/
            //hack around sequelize stupid datetime behavior

            for (let m=0; m < mft_schedules.length; m++){
              mft_schedules[m] = mft_schedules[m].setValuesForDisplay();

            }
              res.render('endpoint_analyst_view', {
                endpoint: endpoint,
                routes: routes,
                endpoint_props: endpoint_props,
                mft_schedules: mft_schedules,
                dateformat: require('dateformat'),
                moment: moment,
              });
            //});
          });

        });
      });

    });
  });
};


exports.get_edit = function (req, res) {
  All_Models.Endpoint.findByPk(req.query.id, {
  }).then(function (endpoint) {
    //console.log(types);
    res.render('endpoint_edit', {
      endpoint: endpoint,
      types: constants.endpoint_types,
      //TODO sync form/views to display values from constants that match alert email labels
      alert_levels: constants.alert_levels,
    });
  });
};

exports.post_edit = function (req, res) {
  console.log(req.body);
  req.body.active = (req.body.active === 'on') ? 1 : 0;

  All_Models.Endpoint.findByPk(req.body.id, {
  }).then(function (endpoint) {
    endpoint.update(req.body).then(function (endpoint) {
      res.redirect('/endpoints/view?id='+endpoint.id);
    });
  });
};

exports.post_search = function (req, res) {
  const Op = Sequelize.Op;
  let e_prop_where = {
    [Op.or]: [
      {
        name: { [Op.like]: '%'+req.body.search+'%'}
      },
      {
        value: { [Op.like]: '%'+req.body.search+'%'}
      }
    ]
  };
  
  
  All_Models.Endpoint_Property.findAll({where: e_prop_where}).then(function (endpoint_props) {
    var consolidated = {};
    var eid = [];
    for (let x = 0; x < endpoint_props.length; x++){
      eid.push(endpoint_props[x].endpoint_id);
      if(consolidated[endpoint_props[x].endpoint_id] !== undefined && consolidated[endpoint_props[x].endpoint_id].hasOwnProperty('properties')){
        consolidated[endpoint_props[x].endpoint_id]['properties'].push(endpoint_props[x]);
      }
      else{
        consolidated[endpoint_props[x].endpoint_id] = {'properties': [endpoint_props[x]]};
      }
    }

    let e_where = {
      [Op.or]: [
        {
          organization: { [Op.like]: '%'+req.body.search+'%'}
        },
        {
          software: { [Op.like]: '%'+req.body.search+'%'}
        },
        {
          doclink: { [Op.like]: '%'+req.body.search+'%'}
        },
        {
          subsystem: { [Op.like]: '%'+req.body.search+'%'}
        },
        {
          description: { [Op.like]: '%'+req.body.search+'%'}
        },
        {
          bw_process_ident: { [Op.like]: '%'+req.body.search+'%'}
        },
        {
          receiving_app: { [Op.like]: '%'+req.body.search+'%'}
        },
        {
          receiving_facility: { [Op.like]: '%'+req.body.search+'%'}
        },
        {
          name: { [Op.like]: '%'+req.body.search+'%'}
        },
        {
          id: { [Op.in]: eid }
        }
      ]
    };
    All_Models.Endpoint.findAll({where: e_where}).then(function (endpoints) {
      for(let i = 0; i < endpoints.length; i++){
        if(consolidated[endpoints[i].id] === undefined){
          consolidated[endpoints[i].id] = {'endpoint': endpoints[i]};
        }else{
          consolidated[endpoints[i].id].endpoint = endpoints[i];
        }
        
      }
      /*if(consolidated[endpoint_props[x].endpoint_id]['endpoint'] === undefined){
        All_Models.Endpoint.findByPk(endpoint_props[x].endpoint_id, {
        }).then(function (endpoint) {
          consolidated[endpoint_props[x].endpoint_id] = {'endpoint': endpoint};
        });
      }
    */
      //console.log(consolidated);
      res.render('endpoint_search', {
        endpoints: consolidated
      });
    });
  });
};

exports.get_delete = function (req, res) {
  const Op = Sequelize.Op;
  All_Models.Endpoint.findByPk(req.query.id, {}).then(function (endpoint) {
    console.log(endpoint);
    //get all routes
    All_Models.Route.findAll({
      where: {
        [Op.or]: [
          {
            producer_id: endpoint.id
          },
          {
            consumer_id: endpoint.id
          }
        ]
      }
    }).then(function (routes) {
      //go through routes and get all props for the routes and criteria
      var rid = [];
      for (let x = 0; x < routes.length; x++) {
        rid.push(routes[x].id);
      }
      All_Models.Route_Property.destroy({
        where: {
          route_id: { [Op.in]: rid }
        }
      }).then(function (rp_affectedRows) {
        All_Models.Route_Criteria.destroy({
          where: {
            route_id: { [Op.in]: rid }
          }
        }).then(function (rc_affectedRows) {
          All_Models.Route.destroy({
            where: {
              id: { [Op.in]: rid }
            }
          }).then(function (r_affectedRows) {
            All_Models.Endpoint_Property.destroy({
              where: {
                endpoint_id: endpoint.id
              }
            }).then(function (ep_affectedRows) {
              All_Models.MFT_Schedule.destroy({
                where: {
                  endpoint_id: endpoint.id
                }
              }).then(function (es_affectedRows) {
                //delete the final endpoint
                endpoint.destroy();
                //build flash message then redirect
                req.flash('success_message', rc_affectedRows+' Route Criteria, '+rp_affectedRows+' Route Props, '+r_affectedRows+' Routes, '+ep_affectedRows+' EndPoint Props, '+es_affectedRows+' EndPoint Schedules and 1 Endpoint Deleted!');
                res.redirect('/endpoints');
              });
            });
          })
        });
      });
    });
  });
};