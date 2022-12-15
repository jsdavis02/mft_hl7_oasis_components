let All_Models = require('../models/all_models');
var env = process.env.NODE_ENV || 'development';
var config = require('../config/config')[env];
var Audit = require('../models/audit');
var Route = require('../models/route');
var RouteProps = require('../models/route_props');
var User = require('../models/user');
var Endpoint = require('../models/endpoint');
// var passport = require('passport');
// require('../config/passport');
const api_helper = require('./api_helper');
//var passport = require('../config/passport');
const request = require('request-promise');
let moment = require('moment');
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


});

exports.get_reprocess = function(req, res) {
  //get audit record
  Audit.findByPk(req.query.id).then(function (audit) {
    //console.log(audit);
    //get the endpoint and endpoint props for the queue 
    let env = "DEV";
    switch (process.env.NODE_ENV) {
      case "test":
        env = "TST";
        break;
      case "production":
        env = "PRD";
        break;
      default:
        break;
    }
    //console.log(route_prop);
    //console.log(audit);
    //build request body
    let r_body = {
      "messageGUID": parseInt(audit.MessageGUID),
      "producer_id": parseInt(audit.producer_id),
      "producer_messagetypemessagecode": audit.MessageTypeMessageCode,
      "producer_messagetypetriggerevent": audit.MessageTypeTriggerEvent,
      "dateTimeReceived": audit.DateTimeofMessage,
      //if we have edited data in post use it otherwise what is in db
      "data": (req.body.MessagePayloadEdit) ? req.body.MessagePayloadEdit : audit.MessagePayload
    };
    const req_options = {
      method: 'POST',
      uri: 'http://'+config.bw.host+':'+config.bw.port+'/reprocessmessage',
      body: r_body,
      json: true,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };

    request(req_options).then(function (response) {
      req.flash('success_message', 'Message with GUID: '+audit.MessageGUID+' was resubmitted to HL7 Routing Engine');
      return res.redirect('/audit');
    }).catch(function (err) {
      req.flash('error_message', err.toLocaleString());
      return res.redirect('/audit');
    })

  });
};

exports.get_resend = function(req, res) {
  //get audit record
  Audit.findByPk(req.query.id).then(function (audit) {
    //console.log(audit);
    //get the endpoint and endpoint props for the queue 
    let env = "DEV";
    switch (process.env.NODE_ENV) {
      case "test":
        env = "TST";
        break;
      case "production":
        env = "PRD";
        break;
      default:
        break;
    }
    //Todo add if clause for mft vs hl7 for resend code
    // if data_format is hl7 do the HL7 resend, else data_format is mft
    if (audit.data_format === 'hl7') {
      Route.findByPk(audit.route_id).then(function (route) {
        RouteProps.findOne({

          where: {
            route_id: audit.route_id,
            env: env,
            name: "outbound_queue"
          }

        }).then(route_prop => {
          //console.log(route_prop);
          //console.log(audit);
          //build request body
          let r_body = {
            "messageGUID": parseInt(audit.MessageGUID),
            "route_id": parseInt(audit.route_id),
            "producer_id": parseInt(route.producer_id),
            "consumer_id": parseInt(route.consumer_id),
            "producer_messagetypemessagecode": route.producer_messagetypemessagecode,
            "producer_messagetypetriggerevent": route.producer_messagetypetriggerevent,
            "consumer_messagetypemessagecode": route.consumer_messagetypemessagecode,
            "consumer_messagetypetriggerevent": route.consumer_messagetypetriggerevent,
            "hasCriteria": route.hasCriteria,
            "dateTimeReceived": audit.DateTimeofMessage,
            "data": (req.body.MessagePayloadEdit) ? req.body.MessagePayloadEdit : audit.MessagePayload,
            "queue": route_prop.value
          };


          const req_options = {
            method: 'POST',
            uri: 'http://' + config.bw.host + ':' + config.bw.port + '/hl7message',
            body: r_body,
            json: true,
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          };

          request(req_options).then(function (response) {
            req.flash('success_message', 'Message with GUID: ' + audit.MessageGUID + ' was resubmitted to Queue: ' + route_prop.value);
            return res.redirect('/audit');
          }).catch(function (err) {
            req.flash('error_message', err.message);
            return res.redirect('/audit');
          })
        })
      });
    } 
    else if (audit.data_format === 'mft') {
      const req_options = {
        method: 'GET',
        uri: 'http://'+config.bw.host+':'+config.bw.mft_port+'/mft_consumer_resend?audit_id='+audit.id,
        body: {},
        json: true,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Authorization': 'Basic YWRtaW46b2FzaXM='
        }
      };
      
      request(req_options).then(function (response) {
        req.flash('success_message', 'Message with GUID: ' + audit.MessageGUID + ' was resubmitted to Consumer: ' + audit.consumer_ident);
        return res.redirect('/audit');
      }).catch(function (err) {
        //console.log(err);
        req.flash('error_message', err.message);
        return res.redirect('/audit');
      })
    }
  });
};

exports.analyst_error_email = function(req, res){
  let nodemailer = require('nodemailer');
  var App_Setting = require('../models/app_settings');
  Audit.findByPk(req.query.id).then(function (audit) {
    App_Setting.findAll({
      where: {
        env: config.env
      }
    }).then(function (app_settings) {
      //console.log(req.user);
      let to_emails = [];
      for (let setting of app_settings){
         //console.log(setting);
        if(setting.name.includes('notification_email')){ to_emails.push(setting.value)}
      }
      let transporter = nodemailer.createTransport(config.email.smtp);
      transporter.sendMail({
        from: 'oasis@valleywisehealth.org',
        to: to_emails.join(', '),
        replyTo: req.user.email,
        subject: 'Analyst Support Request for Oasis: '+config.env,
        text: 'We would like help looking into this Audit Entry! Here is the link: http://'+req.get('host')+'/audit/view?id='+audit.id
      }, (err, info) => {
        if(err){
          req.flash('error_message', 'Email failed to send with error: '+err);  
        }
        else{
          req.flash('success_message', 'Email sent to: '+to_emails.join(', '));
        }
        res.redirect('/audit/analyst');
      });
      //console.log(audit.MessagePayload);
    });
    
  });
};

exports.analyst = function(req, res) {
  //console.log(req.user);
  User.findByPk(req.user.id,{
    include: [{model: Endpoint}]
  }).then(function (user) {
    //console.log(user.endpoints);
    
    //we build the endpoint lists from users associations only
    var producers = [];
    var eids = [];
    //console.log(req.user.role);
 
      
    for(let e=0;e<user.endpoints.length;e++){
      producers.push(user.endpoints[e].bw_process_ident);
      eids.push(user.endpoints[e].id);
    }
    
    var consumers = producers;
    //console.log(eids);
    const Op = Sequelize.Op;
    var page = 1;
    var offset = 0;
    var where = {};
    var apfilters = {
      'type': '',
      'ProcessState': '',
      'MessageTypeMessageCode': '',
      'MessageTypeTriggerEvent': '',
      'producer_ident': '',
      'consumer_ident': ''
    };
    if (req.query.p !== undefined && req.query.p > 0) {
      page = parseInt(req.query.p);
      offset = (page - 1) * 100;
    }
    //console.log(req.query);
    //console.log(Audit.rawAttributes);
    //if search, build where for search not filters
    let pq_parms = '';
    let search_value = '';
    let start_value = moment().subtract(1, 'days').format('YYYY-MM-DD[T]HH:mm');
    let end_value = moment().format('YYYY-MM-DD[T]HH:mm');
    let endpoint_where = {[Op.or]: [{producer_id: {[Op.in]: eids}},{consumer_id: {[Op.in]: eids}}]};
    if(req.user.role === 'admin'){
      endpoint_where = '';
    }
    if(req.query.search !== undefined){
      //console.log(req.query.start+'->'+req.query.end);
      if(req.query.end === undefined){
        req.query.end = moment().format('YYYY-MM-DD[T]HH:mm');
      }
      if(req.query.start === undefined){
        req.query.start = moment().subtract(1, 'days').format('YYYY-MM-DD[T]HH:mm');
      }
      search_value = req.query.search;
      start_value = req.query.start;
      end_value = req.query.end;
      pq_parms += '&' + 'search' + '=' + req.query.search;
      pq_parms += '&' + 'start' + '=' + req.query.start;
      pq_parms += '&' + 'end' + '=' + req.query.end;
      
      date_where = {
        proc_time: {
          [Op.lt]: moment.utc(req.query.end),//.format('YYYY-MM-DD[T]HH:mm'),
          [Op.gt]: moment.utc(req.query.start)//.format('YYYY-MM-DD[T]HH:mm')
        }
      };
      where = {
        [Op.and]: [
          endpoint_where,
            date_where,
          {[Op.or]: [
              {
                type: { [Op.like]: '%'+req.query.search+'%'}
              },
              {
                ProcessState: { [Op.like]: '%'+req.query.search+'%'}
              },
              {
                MessageControlID: { [Op.like]: '%'+req.query.search+'%'}
              },
              {
                MessagePayload: { [Op.like]: '%'+req.query.search+'%'}
              },
              {
                producer_ident: { [Op.like]: '%'+req.query.search+'%'}
              },
              {
                consumer_ident: { [Op.like]: '%'+req.query.search+'%'}
              },
              {
                description: { [Op.like]: '%'+req.query.search+'%'}
              }
            ]}
        ]
      };
    }else{
      where = endpoint_where;
      if(req.user.role === 'admin'){
        where = {};
      }
      for (const qk in req.query) {
        for (const key in Audit.rawAttributes) {
          if (qk == key) {
            console.log(req.query[qk]);
            where[key] = req.query[qk];
            pq_parms += '&' + key + '=' + req.query[qk];
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
      console.log(where);
    }
    console.log(where);
    /*
    const req_options = {
      method: 'GET',
      uri: 'http://'+config.bw.host+':'+config.bw.ops_port+'/bwapps?appspace=Oasis-HL7&domain=OASIS',
      json: true,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };
    */
      Audit.findAll({
        where: where,
        'limit': 100,
        'offset': offset,
        'order': [['proc_time', 'DESC'], ['MessageGUID', 'DESC'], ['created_at', 'ASC']]
      }).then(function (audits) {
        sequelize.query('select distinct ProcessState from audit', {
          model: Audit,
          mapToModel: true // pass true here if you have any mapped fields
        }).then(process_states => {
          sequelize.query('select distinct type from audit', {
            model: Audit,
            mapToModel: true // pass true here if you have any mapped fields
          }).then(types => {
            // sequelize.query('select distinct MessageTypeMessageCode from audit', {
            //   model: Audit,
            //   mapToModel: true
            // }).then(message_types => {
            //   sequelize.query('select distinct MessageTypeTriggerEvent from audit', {
            //     model: Audit,
            //     mapToModel: true
            //   }).then(message_triggers => {
                if(req.user.role === 'admin') {
                  sequelize.query('select distinct producer_ident from audit order by producer_ident ASC', {
                    model: Audit,
                    mapToModel: true
                  }).then(producers => {
                    sequelize.query('select distinct consumer_ident from audit order by consumer_ident ASC', {
                      model: Audit,
                      mapToModel: true
                    }).then(consumers => {
                      var pdcr = []; 
                      var cnsmr = [];
                      for (let e = 0; e < producers.length; e++) {
                        console.log(producers[e]);
                        pdcr.push(producers[e].producer_ident);
                      }
                      for (let e = 0; e < consumers.length; e++) {
                        cnsmr.push(consumers[e].consumer_ident  );
                      }
                      producers = pdcr;
                      consumers = cnsmr;
                      res.render('audit_analyst', {
                        audits: audits, //send map by guid for output loop
                        p: page,
                        pq_parms: pq_parms,
                        search_value: search_value,
                        start_value: start_value,
                        end_value: end_value,
                        wparms: where,
                        appendfilters: apfilters,
                        error_message: req.flash('error_message'),
                        success_message: req.flash('success_message'),
                        process_states: process_states,
                        types: types,
                        message_types: [],
                        message_triggers: [],
                        producers: producers,
                        consumers: consumers,
                        moment: moment
                      });
                    });
                  });
                }
                else{
                  res.render('audit_analyst', {
                    audits: audits, //send map by guid for output loop
                    p: page,
                    pq_parms: pq_parms,
                    search_value: search_value,
                    start_value: start_value,
                    end_value: end_value,
                    wparms: where,
                    appendfilters: apfilters,
                    error_message: req.flash('error_message'),
                    success_message: req.flash('success_message'),
                    process_states: process_states,
                    types: types,
                    message_types: [],
                    message_triggers: [],
                    producers: producers,
                    consumers: consumers
                  });
                }
              });
            });
          });
        });
  //     });
  //  
  // });
};
exports.index = function(req, res) {
  //console.log(Intl.DateTimeFormat().resolvedOptions().timeZone);
  const Op = Sequelize.Op;
  var page = 1;
  var offset = 0;
  var where = {};
  var apfilters = {
    'type': '',
    'ProcessState': '',
    'MessageTypeMessageCode': '',
    'MessageTypeTriggerEvent': '',
    'producer_ident': '',
    'consumer_ident': ''
  };
  if (req.query.p !== undefined && req.query.p > 0) {
    page = parseInt(req.query.p);
    offset = (page - 1) * 100;
  }
  //console.log(req.query);
  //console.log(Audit.rawAttributes);
  //if search, build where for search not filters
  let pq_parms = '';
  let search_value = '';
  let start_value = moment().subtract(1, 'days').format('YYYY-MM-DD[T]HH:mm');
  let end_value = moment().format('YYYY-MM-DD[T]HH:mm');
  if(req.query.search !== undefined){
    //console.log(req.query.search);
    if(req.query.end === undefined){
      req.query.end = moment().format('YYYY-MM-DD[T]HH:mm');
    }
    if(req.query.start === undefined){
      req.query.start = moment().subtract(1, 'days').format('YYYY-MM-DD[T]HH:mm');
    }
    search_value = req.query.search;
    start_value = req.query.start;
    end_value = req.query.end;
    pq_parms += '&' + 'search' + '=' + req.query.search;
    pq_parms += '&' + 'start' + '=' + req.query.start;
    pq_parms += '&' + 'end' + '=' + req.query.end;
    //console.log(req.query.search.length);
    if(req.query.search.length <= 0){
      //console.log(req.query.start+'->'+req.query.end);
      where = {
        proc_time: {
          [Op.lt]: moment.utc(req.query.end),//.format('YYYY-MM-DD[T]HH:mm'),
          [Op.gt]: moment.utc(req.query.start)//.format('YYYY-MM-DD[T]HH:mm')
        }
      };
    }
    else {
      where = {
        [Op.and]: [
          {
            proc_time: {
              [Op.lt]: moment(req.query.end),//.format('YYYY-MM-DD[T]HH:mm'),
              [Op.gt]: moment(req.query.start)//.format('YYYY-MM-DD[T]HH:mm')
            }
          },
          {
            [Op.or]: [
              {
                type: {[Op.like]: '%' + req.query.search + '%'}
              },
              {
                ProcessState: {[Op.like]: '%' + req.query.search + '%'}
              },
              {
                MessageControlID: {[Op.like]: '%' + req.query.search + '%'}
              },
              {
                MessagePayload: {[Op.like]: '%' + req.query.search + '%'}
              },
              {
                producer_ident: {[Op.like]: '%' + req.query.search + '%'}
              },
              {
                consumer_ident: {[Op.like]: '%' + req.query.search + '%'}
              },
              {
                description: {[Op.like]: '%' + req.query.search + '%'}
              }
            ]
          }]
      };
    }
  }else{
    for (const qk in req.query) {
      for (const key in Audit.rawAttributes) {
        if (qk == key) {
          where[key] = req.query[qk];
          pq_parms += '&' + key + '=' + req.query[qk];
        }
        else {
          //here we put all the parms that are not this key as a string to append
          // to each url filter so we can do combinations so
          // apfilters['active'] = direction=producer&type=HL7
          console.log(apfilters[key]);
          if(apfilters.hasOwnProperty(key) && apfilters[key].length > 0){
            apfilters[key] = apfilters[key]+'&'+qk+'='+req.query[qk];
          }
          else{
            apfilters[key] = qk+'='+req.query[qk];
          }
        }
      }
    }
  }
  
  console.log(pq_parms);
  Audit.findAll({
    where: where,
    limit: 100,
    offset: offset,
    order: [['id', 'DESC']]
    //TODO the below with time columns in the order by clause is causing queries to go from 24 MS to 24 S!!
    //'order': [['proc_time', 'DESC'], ['MessageGUID', 'DESC'], ['created_at', 'ASC']]
  }).then(function (audits) {
    sequelize.query('select distinct ProcessState from audit', {
      model: Audit,
      mapToModel: true // pass true here if you have any mapped fields
    }).then(process_states => {
      sequelize.query('select distinct type from audit', {
        model: Audit,
        mapToModel: true // pass true here if you have any mapped fields
      }).then(types => {
        // sequelize.query('select distinct MessageTypeMessageCode from audit', {
        //   model: Audit,
        //   mapToModel: true
        // }).then(message_types => {
        //   sequelize.query('select distinct MessageTypeTriggerEvent from audit', {
        //     model: Audit,
        //     mapToModel: true
        //   }).then(message_triggers => {
            sequelize.query('select distinct producer_ident from audit order by producer_ident ASC', {
              model: Audit,
              mapToModel: true
            }).then(producers => {
              sequelize.query('select distinct consumer_ident from audit order by consumer_ident ASC', {
                model: Audit,
                mapToModel: true
              }).then(consumers =>
                  res.render('audit', {
                    audits: audits, //send map by guid for output loop
                    p: page,
                    pq_parms: pq_parms,
                    search_value: search_value,
                    start_value: start_value,
                    end_value: end_value,
                    wparms: where,
                    appendfilters: apfilters,
                    error_message: req.flash('error_message'),
                    success_message: req.flash('success_message'),
                    process_states: process_states,
                    types: types,
                    message_types: [],
                    message_triggers: [],
                    producers: producers,
                    consumers: consumers,
                    moment: moment,
                  }));
            });
          });
        });
      });
  //   });
  // });
};
exports.get_audit_file = function (req, res) {
  All_Models.Audit_Property.findByPk(req.query.audit_prop_id, {
    }).then(function (audit_prop) {
    res.download(req.query.fpath, audit_prop.value);
  });
};

exports.analyst_get_audit_file = function (req, res) {
  if(req.query.audit_prop_id === undefined){
    res.redirect('/auth/login');
  }
  All_Models.Audit_Property.findByPk(req.query.audit_prop_id, {
  }).then(function (audit_prop) {
    //
  
    Audit.findByPk(audit_prop.audit_id).then(function (audit) {
      User.findByPk(req.user.id,{
        include: [{model: Endpoint}]
      }).then(function (user) {
        //console.log(user.endpoints);
        //we build the endpoint lists from users associations only
        var producers = [];
        var eids = [];
        for(let e=0;e<user.endpoints.length;e++){
          producers.push(user.endpoints[e].bw_process_ident);
          eids.push(user.endpoints[e].id);
        }
        
        if(eids.includes(audit.producer_id) || eids.includes(audit.consumer_id)){
          res.download(req.query.fpath, audit_prop.value);
        }
        else{
          res.redirect('/auth/login');
        }
      });
    });
  });
};
exports.analyst_get_view = function (req, res) {
  Audit.findByPk(req.query.id).then(function (audit) {
    //console.log(audit.MessagePayload);
    All_Models.Audit_Property.findAll(
        {
          where: {audit_id: req.query.id},
          order: [['name', 'ASC']]
        }
    ).then(function (audit_props) {
      
      try {
        audit.MessagePayload = JSON.stringify(JSON.parse(audit.MessagePayload), undefined, 2);
      } catch (e) {
        console.log('payload is not json')
      }
      //console.log(audit.MessagePayload);
      res.render('analyst_audit_view', {
        audit: audit,
        audit_props: audit_props
      });
    });
  });
};

exports.get_view = function (req, res) {
  All_Models.Audit.findByPk(req.query.id).then(function (audit) {
    //console.log(audit.MessagePayload);
    All_Models.Audit_Property.findAll(
        {
          where: {audit_id: req.query.id},
          order: [['name', 'ASC']]
        }
    ).then(function (audit_props) {
      
    try {
      audit.MessagePayload = JSON.stringify(JSON.parse(audit.MessagePayload), undefined, 2);
    } catch (e) {
      console.log('payload is not json')
    }
    
      //console.log(audit.MessagePayload);
      res.render('audit_view', {
        audit: audit,
        audit_props: audit_props
      });
    });
  });
};  

exports.get_payload = function (req, res) {
  Audit.findByPk(req.query.id).then(function (audit) {
    //console.log(audit.MessagePayload);
    try {
      audit.MessagePayload = JSON.stringify(JSON.parse(audit.MessagePayload), undefined, 2);
    } catch (e) {
      console.log('payload is not json')
    }
    res.render('payload_edit', {
      audit: audit,
      action: req.query.action //grab the action we pass in link, hand to our view
    });
  });
};

exports.post_payload = function (req, res) {
  console.log(req.body);
  Audit.findByPk(req.query.id).then(function (audit) {
    audit.update(req.body).then(function (audit) {
      res.redirect('audit_view', {
        audit: audit
      });
    });
  });
};

