let All_Models = require('../models/all_models');

var env = process.env.NODE_ENV || 'development';
var config = require('../config/config')[env];
/*
var Route = require('../models/route');
var Endpoint = require('../models/endpoint');
var Route_Property = require('../models/route_props');
var Route_Criteria = require('../models/route_criterias');
*/
let constants = require('../config/constants');
var messagetypes = constants.messagetypes;
var triggerevents = constants.triggerevents;

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
  

exports.index = function (req, res) {
  var where = {};
  var apfilters = {
    'active': '',
    'type': '',
    'producer_id': '',
    'consumer_id': '',
    'producer_messagetypemessagecode': '',
    'producer_messagetypetriggerevent': '',
    'consumer_messagetypemessagecode': '',
    'consumer_messagetypetriggerevent': '',
    'hasCriteria': '',
    'hasSplit': '',
    'hasTranslation': ''
  };
  for (const qk in req.query) {
    for (const key in All_Models.Route.rawAttributes) {
      if (qk === key) {
        where[key] = req.query[qk]
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

  All_Models.Route.findAll({where: where, order: [['id','DESC']], include: [{model: All_Models.Endpoint, as: 'Producer',}, {model: All_Models.Endpoint, as: 'Consumer'}]}).then(function (routes) {
    All_Models.Endpoint.findAll({attributes: ['id', 'bw_process_ident'], where: {direction: 'producer'},order: [['bw_process_ident', 'ASC']]}).then(function (producers) {
      All_Models.Endpoint.findAll({attributes: ['id', 'bw_process_ident'], where: {direction: 'consumer'},order: [['bw_process_ident', 'ASC']]}).then(function (consumers) {
        sequelize.query('select distinct producer_messagetypemessagecode from routes', {
          model: All_Models.Route,
          mapToModel: true
        }).then(producer_message_types => {
          sequelize.query('select distinct producer_messagetypetriggerevent from routes', {
            model: All_Models.Route,
            mapToModel: true
          }).then(producer_message_events => {
            sequelize.query('select distinct consumer_messagetypemessagecode from routes', {
              model: All_Models.Route,
              mapToModel: true
            }).then(consumer_message_types => {
              sequelize.query('select distinct consumer_messagetypetriggerevent from routes', {
                model: All_Models.Route,
                mapToModel: true
              }).then(consumer_message_events =>
                  res.render('route', {
                    routes: routes, //send map by guid for output loop
                    wparms: where,
                    appendfilters: apfilters,
                    producers: producers,
                    consumers: consumers,
                    producer_message_types: producer_message_types,
                    producer_message_events: producer_message_events,
                    consumer_message_types: consumer_message_types,
                    consumer_message_events: consumer_message_events
                  }));
            });
          });
        });
      });
    });
  });
};

exports.get_create = function (req, res) {
  All_Models.Endpoint.findAll({order: [['name', 'ASC']]}).then(function (endpoints) {
    res.render('route_add', {
      endpoints: endpoints,
      messagetypes: messagetypes,
      triggerevents: triggerevents,
      producer_id: req.query.producer_id,
      consumer_id: req.query.consumer_id
    });
  });
};

exports.post_create = function (req, res) {
  //we have to split trigger event for db storage
  p = req.body.producer_messagetypetriggerevent.split('.');
  c = req.body.consumer_messagetypetriggerevent.split('.');
  req.body.producer_messagetypemessagecode = p[0];
  req.body.consumer_messagetypemessagecode = c[0];
  req.body.producer_messagetypetriggerevent = p[1];
  req.body.consumer_messagetypetriggerevent = c[1];
  //fix checkbox to boolean
  req.body.active = (req.body.active === 'on') ? 1 : 0;
  req.body.hasCriteria = (req.body.hasCriteria === 'on') ? 1 : 0;
  req.body.hasTranslation = (req.body.hasTranslation === 'on') ? 1 : 0;
  req.body.hasSplit = (req.body.hasSplit === 'on') ? 1 : 0;
  All_Models.Route.create(req.body).then(route => {
    res.redirect('/routes/view?id=' + route.id);
  });
};

exports.get_create_many = function (req, res) {
  All_Models.Endpoint.findAll().then(function (endpoints) {
    res.render('route_add_many', {
      endpoints: endpoints,
      messagetypes: messagetypes,
      triggerevents: triggerevents
    });
  });
};

exports.post_create_many = function (req, res) {
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
  //console.log(req);
  //build array then will do bulk create so callback redirect
  //is called after loop complete
  let bulkRouteArray = [];
  if(typeof(req.body.messagetypes) === 'string'){
    //fix when bulk add was used for a single
    req.body.messagetypes = [req.body.messagetypes];
  }
  //console.log(typeof(req.body.messagetypes));
  //console.log(req.body.messagetypes);
  //console.log(req.body.messagetypes.length);
  for (let i = 0; i < req.body.messagetypes.length; i++) {
    //console.log(req.body.messagetypes[i]);
    let messagetypesplit = req.body.messagetypes[i].split('.');
    //console.log(messagetypesplit);
    //console.log(req.body.messagetypes);
    //console.log(req.body.messagetypes.length);
    bulkRouteArray.push({
      type: 'HL7',
      producer_id: req.body.producer_id,
      consumer_id: req.body.consumer_id,
      producer_messagetypemessagecode: messagetypesplit[0],
      producer_messagetypetriggerevent: messagetypesplit[1],
      consumer_messagetypemessagecode: messagetypesplit[0],
      consumer_messagetypetriggerevent: messagetypesplit[1],
      hasCriteria: (req.body.hasCriteria) ? 1 : 0,
      hasTranslation: (req.body.hasTranslation) ? 1 : 0,
      hasSplit: (req.body.hasSplit) ? 1 : 0,
      active: false
    });
    
  }
  //loop and use single create since we want to add props otherwise do bulk
  //console.log(bulkRouteArray);
  if(req.body.addProps === 'on'){
    bulkRouteArray.forEach(function (route_array) {
      console.log(route_array);
      let r_props = [];
      All_Models.Route.create(route_array).then(function (new_route) {
        console.log(new_route);
        if (new_route.hasCriteria){
          r_props.push({
            route_id: new_route.id,
            name: 'criteria_script',
            value: 'route_'+new_route.id+'_'+new_route.producer_messagetypetriggerevent+'_criteria.py',
            env: env
          });
        }
        if (new_route.hasTranslation){
          r_props.push({
            route_id: new_route.id,
            name: 'translate_script',
            value: 'route_'+new_route.id+'_'+new_route.producer_messagetypetriggerevent+'_wrapper.py',
            env: env
          });
        }
        if (new_route.hasSplit){
          r_props.push({
            route_id: new_route.id,
            name: 'split_script',
            value: 'route_'+new_route.id+'_'+new_route.producer_messagetypetriggerevent+'_wrapper.py',
            env: env
          });
          All_Models.Endpoint.findByPk(new_route.consumer_id).then(function (endpoint) {
            r_props.push({
              route_id: new_route.id,
              name: 'split_bw_ident',
              value: endpoint.bw_process_ident,
              env: env
            });
            console.log(r_props);
            All_Models.Route_Property.bulkCreate(r_props).then(function () {
              res.redirect('/routes');
            });
          });
          
        }
        else{
          //hl7 routes if not a split have outbound queue
          All_Models.Endpoint.findByPk(new_route.consumer_id).then(function (endpoint) {
            r_props.push({
              route_id: new_route.id,
              name: 'outbound_queue',
              value: 'oasis.hl7.'+endpoint.bw_process_ident+'.outbound',
              env: env  
            });
            console.log(r_props);
            All_Models.Route_Property.bulkCreate(r_props).then(function () {
              res.redirect('/routes');
            });
          });
        }
        
      })
    });
  }
  else{
    All_Models.Route.bulkCreate(bulkRouteArray).then(() => {
      res.redirect('/routes');
    });
  }
  
};

exports.get_view = function (req, res) {
  All_Models.Route.findByPk(req.query.id, {
    include: [{
      model: All_Models.Endpoint,
      as: 'Producer',
      //where: { producer_id: Sequelize.col('endpoint.id')}
    },
      {
        model: All_Models.Endpoint,
        as: 'Consumer'
      }]
  }).then(function (route) {
    All_Models.Route_Property.findAll({
      where: {
        route_id: req.query.id
      }
    }).then(function (route_props) {
      for(let i=0; i < route_props.length; i++) {
        if (route_props[i].name.includes("password") || route_props[i].name.includes("passphrase")){
          route_props[i].value = "*****";
        }
      }
      All_Models.Route_Criteria.findAll({
        where: {
          route_id: req.query.id
        }
      }).then(function (route_criterias) {
          res.render('route_view', {
            route: route,
            route_props: route_props,
            route_criterias: route_criterias,
          });
      });

    })

  })
};

exports.get_analyst_view = function (req, res) {
  All_Models.Route.findByPk(req.query.id, {
    include: [{
      model: All_Models.Endpoint,
      as: 'Producer',
      //where: { producer_id: Sequelize.col('endpoint.id')}
    },
      {
        model: All_Models.Endpoint,
        as: 'Consumer'
      }]
  }).then(function (route) {
    All_Models.Route_Property.findAll({
      where: {
        route_id: req.query.id
      }
    }).then(function (route_props) {
      for(let i=0; i < route_props.length; i++) {
        if (route_props[i].name.includes("password") || route_props[i].name.includes("passphrase")){
          route_props[i].value = "*****";
        }
      }
      All_Models.Route_Criteria.findAll({
        where: {
          route_id: req.query.id
        }
      }).then(function (route_criterias) {
        res.render('route_analyst_view', {
          route: route,
          route_props: route_props,
          route_criterias: route_criterias,
        });
      });

    })

  })
};

exports.get_edit = function (req, res) {
  All_Models.Route.findByPk(req.query.id, {
    include: [{
      model: All_Models.Endpoint,
      as: 'Producer',
      //where: { producer_id: Sequelize.col('endpoint.id')}
    },
      {
        model: All_Models.Endpoint,
        as: 'Consumer'
      }]
  }).then(function (route) {
    All_Models.Endpoint.findAll().then(function (endpoints) {
      All_Models.Route_Property.findAll({
        where: {
          route_id: req.query.id
        }
      }).then(function (route_props) {
        res.render('route_edit', {
          route: route,
          route_props: route_props,
          endpoints: endpoints,
          messagetypes: messagetypes,
          triggerevents: triggerevents
        });
      });
    });
  })
};

exports.post_edit = function (req, res) {
  console.log(req.body);
  All_Models.Route.findByPk(req.body.id, {
      include: [{
        model: All_Models.Endpoint,
        as: 'Producer',
        //where: { producer_id: Sequelize.col('endpoint.id')}
      },
        {
          model: All_Models.Endpoint,
          as: 'Consumer'
        }]}
  ).then(function (route) {
    //we have to split trigger event for db storage
    p = req.body.producer_messagetypetriggerevent.split('.');
    c = req.body.consumer_messagetypetriggerevent.split('.');
    req.body.producer_messagetypemessagecode = p[0];
    req.body.consumer_messagetypemessagecode = c[0];
    req.body.producer_messagetypetriggerevent = p[1];
    req.body.consumer_messagetypetriggerevent = c[1];
    //lets generate name field if not specified
    if(req.body.name === undefined || req.body.name.length <= 0){
      req.body.name = route.Producer.bw_process_ident+'-'+ p[0]+'-'+ p[1]+'-'+route.Consumer.bw_process_ident+'-'+c[0]+'-'+c[1];
    }
    //fix checkbox to boolean
    req.body.active = (req.body.active == 'on') ? 1 : 0;
    req.body.hasCriteria = (req.body.hasCriteria) ? 1 : 0;
    req.body.hasTranslation = (req.body.hasTranslation) ? 1 : 0;
    req.body.hasSplit = (req.body.hasSplit) ? 1 : 0;
    //console.log(req.body);
    route.update(req.body).then(function (route) {
      res.redirect('/routes/view?id=' + route.id);
    });
  });
};

exports.get_delete = function (req, res) {
  All_Models.Route.findByPk(req.query.id, {}).then(function (route) {
    //let endpoint_id = endpoint_prop.endpoint_id;
    All_Models.Route_Property.destroy({
      where: {
        route_id: route.id
      }
    }).then(function () {
      All_Models.Route_Criteria.destroy({
        where: {
          route_id: route.id
        }
      }).then(function () {
        route.destroy().then(route => {
          if(req.query.endpoint_id){
            res.redirect('/endpoints/view?id='+req.query.endpoint_id);
          }
          else{
            res.redirect('/routes/');
          }
        })
      });
      
    });
  });
};

exports.post_search = function (req, res) {
  const Op = Sequelize.Op;
  let r_prop_where = {
    [Op.or]: [
      {
        name: { [Op.like]: '%'+req.body.search+'%'}
      },
      {
        value: { [Op.like]: '%'+req.body.search+'%'}
      }
    ]
  };
  All_Models.Route_Property.findAll({where: r_prop_where}).then(function (route_props) {
    var consolidated = {};
    var rid = [];
    for (let x = 0; x < route_props.length; x++){
      rid.push(route_props[x].route_id);
      if(consolidated[route_props[x].route_id] !== undefined && consolidated[route_props[x].route_id].hasOwnProperty('properties')){
        consolidated[route_props[x].route_id]['properties'].push(route_props[x]);
      }
      else{
        consolidated[route_props[x].route_id] = {'properties': [route_props[x]]};
      }
    }
    let r_where = {
      [Op.or]: [
        {
          name: { [Op.like]: '%'+req.body.search+'%'}
        },
        {
          description: { [Op.like]: '%'+req.body.search+'%'}
        },
        {
          id: { [Op.in]: rid }
        }
      ]
    };
    All_Models.Route.findAll({where: r_where}).then(function (routes) {
      for(let i = 0; i < routes.length; i++){
        if(consolidated[routes[i].id] === undefined){
          consolidated[routes[i].id] = {'route': routes[i]};
        }else{
          consolidated[routes[i].id].route = routes[i];
        }

      }
      res.render('route_search', {
        routes: consolidated
      });
    });
    
  });
  
};