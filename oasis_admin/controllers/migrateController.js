var Route = require('../models/route');
var env = process.env.NODE_ENV || 'development';
var config = require('../config/config')[env];
var Endpoint = require('../models/endpoint');
var Route_Property = require('../models/route_props');
var Endpoint_Property = require('../models/endpoint_props');
var Route_Criteria = require('../models/route_criterias');
let MFT_Schedule = require('../models/mft_schedule');
let constants = require('../config/constants');
var moment = require('moment');
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
const Op = Sequelize.Op;
const fs = require('fs');

exports.index = function (req, res) {
  res.render('migrate', {
    route_types: constants.route_types,
    endpoint_types: constants.endpoint_types
  });
};

exports.post_export_file_gen = function (req, res) {
  console.log(req.body);
  let fs = require("fs");
  let ftstamp = moment().format('YYYY-MM-DD-HH-mm-ss');
  let fpath = './migration/exports/export_'+ftstamp+'.json.txt';
  let exportJSON = {};
  let propIDS = [], mItems = [], routeIDS = [], epIDS = [], schedIDS = [];
  
  //fix if single main item
  if(typeof(req.body.mainitems) === 'string')
  {
    mItems.push(req.body.mainitems);
  }
  else{
    mItems = req.body.mainitems;
  }
  
  if(req.body.main_item_type === 'Endpoint'){
    //push all props for endpoints selected ids to array
    Object.keys(req.body).forEach(function (key) {
      //grab selected routes
      if(key.startsWith("route_")){
        routeIDS.push(key.split("_")[1]);
      }
      
    });
    Endpoint.findAll({
      where: {id: {[Op.in]: mItems}},
      include: [{
        model: Endpoint_Property,
        as: 'properties',
        //this causes inner joins so don't do
        //where: {id: {[Op.in]: propIDS}}
      },
      {
        model: MFT_Schedule,
        as: 'schedules',
        //where: {id: {[Op.in]: schedIDS}}
      }]
    }).then(function (endpoints) {
      
      exportJSON.endpoints = endpoints;
      Route.findAll({
        where: {id: {[Op.in]: routeIDS}},
        include: [{
          model: Route_Property,
          as: 'properties',
        },
        {
          model: Route_Criteria,
          as: 'crits',
        }]
      }).then(function (routes) {
        exportJSON.routes = routes;
        //console.log(exportJSON);
        //console.log(exportJSON.endpoints);
        fs.writeFile(fpath, JSON.stringify(exportJSON), (err) => {
          res.download(fpath);
        });
      });
     
    });
  }
  else {
    //main item is routes
    Object.keys(req.body).forEach(function (key) {
      //grab selected endpoints
      if(key.startsWith("endpoint_")){
        epIDS.push(key.split("_")[1]);
      }
    });
    Route.findAll({
      where: {id: {[Op.in]: mItems}},
      include: [{
        model: Route_Property,
        as: 'properties',
        // causes inner joins, instead filter later
        // where: {id: {[Op.in]: propIDS}}
      },
      {
        model: Route_Criteria,
        as: 'crits'
      }]
    }).then(function (routes) {
      //console.log(endpoints);
      exportJSON.routes = routes;
      
      Endpoint.findAll({
        where: {id: {[Op.in]: epIDS}},
        include: [{
          model: Endpoint_Property,
          as: 'properties',
        },
        {
          model: MFT_Schedule,
          as: 'schedules'
        }]
      }).then(function (endpoints) {
        exportJSON.endpoints = endpoints;
        fs.writeFile(fpath, JSON.stringify(exportJSON), (err) => {
          res.download(fpath);
        });
      });
    });
  } 
};

exports.post_import = function (req, res) {
  fs.readFile(req.body.import_file, (err, data) => {
    if (err) throw err;
    let importObj = JSON.parse(data);
    //console.log(importObj);
    //console.log(req.body);
    let toImport = {"endpoints": [], "eprops": {}, "escheds": {}, "routes": [], "rprops": {}, "rcrits": {}};
    let bw_idents = [];
    Object.keys(req.body).forEach(function (key) {
      if(key.startsWith("rconsumer_") || key.startsWith("rproducer_")){
        bw_idents.push(req.body[key]);
      }
      
      if(key.startsWith("endpoint_")){
        toImport.endpoints.push(key.split("_")[1]);
      }
      if(key.startsWith("ep_")){
        if(!toImport.eprops.hasOwnProperty(key.split("_")[1])){
          toImport.eprops[key.split("_")[1]] = [];
        }
        toImport.eprops[key.split("_")[1]].push(key.split("_")[3]);
      }
      if(key.startsWith("es_")){
        if(!toImport.escheds.hasOwnProperty(key.split("_")[1])){
          toImport.escheds[key.split("_")[1]] = [];
        }
        toImport.escheds[key.split("_")[1]].push(key.split("_")[3]);
      }
      if(key.startsWith("route_")){
        toImport.routes.push(key.split("_")[1]);
      }
      if(key.startsWith("rp_")){
        if(!toImport.rprops.hasOwnProperty(key.split("_")[1])){
          toImport.rprops[key.split("_")[1]] = [];
        }
        toImport.rprops[key.split("_")[1]].push(key.split("_")[3]);
      }
      if(key.startsWith("rc_")){
        if(!toImport.rcrits.hasOwnProperty(key.split("_")[1])){
          toImport.rcrits[key.split("_")[1]] = [];
        }
        toImport.rcrits[key.split("_")[1]].push(key.split("_")[3]);
      }
    });
    //console.log('176');
    //console.log(toImport);
    //import endpoints selected first
    bulkEndpoints = [];
    if(importObj.endpoints.length > 0) {
      importObj.endpoints.forEach(function (endpoint) {
        //console.log('182');
        //console.log(endpoint);
        if (toImport.endpoints.includes(endpoint.id)) { //should be an includes
          //endpoint was selected to import
          let e = {};
          for (const k in endpoint) {

            if (k !== 'id' && k !== 'properties' && k !== 'schedules') {
              //console.log(k);
              e[k] = endpoint[k];
            }
            e.bw_process_ident = req.body['bwendpoint_' + endpoint.id];
          }
          //then e props
          //console.log('191');
          //console.log(e);
          bulkEprops = [];
          endpoint.properties.forEach(function (prop) {
            if (toImport.eprops.hasOwnProperty(endpoint.id)) {
              //console.log('212');
              //console.log(prop.id);
              //console.log(toImport.eprops[endpoint.id]);
              if (toImport.eprops[endpoint.id].includes(prop.id)) {
                let p = {};
                for (const pk in prop) {
                  if (pk !== 'id' && pk !== 'endpoint_id') {
                    p[pk] = prop[pk];
                  }
                }
                //console.log('215');
                //console.log(p);
                bulkEprops.push(p);
              }
            }
          });
          e['properties'] = bulkEprops;

          //then schedules
          bulkEscheds = [];
          //console.log('211');
          //console.log(endpoint.schedules);
          endpoint.schedules.forEach(function (sched) {
            if (toImport.escheds.hasOwnProperty(endpoint.id)) {
              if (toImport.escheds[endpoint.id].includes(sched.id)) {
                let s = {
                  'spec_date': null,
                  'spec_time': null,
                  'sub_day_start_time': null,
                  'sub_day_end_time': null,
                };
                for (const sk in sched) {
                 
                  if (sk !== 'id' && sk !== 'endpoint_id' && sk !== 'last_run' && sk !== 'last_files_found') {
                    
                    //fix dates cause node.js is stupid
                    //console.log(sched[sk])
                    if(sk==='spec_date' && sched[sk] != null){
                      sched[sk] = moment.utc(sched[sk]).format('YYYY-MM-DD');
                    }
                    if(sk==='spec_time' && sched[sk] != null){
                      // console.log('253')
                      // console.log(sk);
                      // console.log(sched[sk]);
                      sched[sk] = moment(sched[sk], moment.HTML5_FMT.DATETIME_LOCAL_MS).format('HH:mm:ss');
                      // console.log(sched[sk]);
                    }
                    //console.log(sched[sk])
                    if(sk==='pause_start' && sched[sk] != null){
                      sched[sk] = moment(sched[sk], moment.HTML5_FMT.DATETIME_LOCAL_MS).format('YYYY-MM-DD HH:mm:ss');
                    }
                    if(sk==='pause_end' && sched[sk] != null){
                      sched[sk] = moment(sched[sk], moment.HTML5_FMT.DATETIME_LOCAL_MS).format('YYYY-MM-DD HH:mm:ss');
                    }
                    if(sk==='sub_day_start_time' && sched[sk] != null){
                      sched[sk] = moment(sched[sk], moment.HTML5_FMT.DATETIME_LOCAL_MS).format('HH:mm:ss');
                    }
                    if(sk==='sub_day_end_time' && sched[sk] != null){
                      //console.log(sk);
                      //console.log(sched[sk]);
                      sched[sk] = moment(sched[sk], moment.HTML5_FMT.DATETIME_LOCAL_MS).format('HH:mm:ss');
                      //console.log(sched[sk]);
                    }
                    s[sk] = sched[sk];
                  }
                }
                //console.log('277');
                //console.log(s);
                bulkEscheds.push(s);
              }
            }
          });
          e['schedules'] = bulkEscheds;

          bulkEndpoints.push(e);
        }
      });
    }
    //console.log('228');
    //console.log(bulkEndpoints);
    //console.log(bulkEndpoints[0].properties);
    
    
    //routes associating as selected
    bulkRoutes = [];
    //console.log('234');
    //console.log(importObj.routes);
    if(importObj.routes.length > 0) {
      importObj.routes.forEach(function (route) {
        if (toImport.routes.includes(route.id)) {
          //route was selected to import
          let r = {};
          for (const k in route) {
            //ignore id's
            if (k !== 'id' && k !== 'properties' && k !== 'crits' && k !== 'producer_id' && k !== 'consumer_id') {
              //we will get the producer and consumer id's after endpoint save by bw ident.
              r[k] = route[k];
            }
            if (k === 'producer_id') {
              //temporarily lets set these to the selected bw ident while we have the route id
              //for later replacement after endpoint save
              r[k] = req.body['rproducer_' + route.id + '_producer_id'];
            }
            if (k === 'consumer_id') {
              //temporarily lets set these to the selected bw ident while we have the route id
              //for later replacement after endpoint save
              r[k] = req.body['rconsumer_' + route.id + '_consumer_id'];
            }
          }
          //console.log('246');
          //console.log(r);
          //then r props
          bulkRprops = [];
          route.properties.forEach(function (prop) {
            if (toImport.rprops.hasOwnProperty(route.id)) {
              if (toImport.rprops[route.id].includes(prop.id)) {
                let p = {};
                for (const pk in prop) {
                  if (pk !== 'id' && pk !== 'route_id') {
                    p[pk] = prop[pk];
                  }
                }
                bulkRprops.push(p);
              }
            }
          });
          r['properties'] = bulkRprops;

          //then crits
          bulkRcrits = [];
          route.crits.forEach(function (crit) {
            if (toImport.rcrits.hasOwnProperty(route.id)) {
              if (toImport.rcrits[route.id].includes(crit.id)) {
                let s = {};
                for (const sk in crit) {
                  if (sk !== 'id' && sk !== 'route_id') {
                    s[sk] = crit[sk];
                  }
                }
                bulkRcrits.push(s);
              }
            }
          });
          r['crits'] = bulkRcrits;

          bulkRoutes.push(r);
        }
      });
    }
    //console.log('285');
    //console.log(bulkRoutes);
    let new_endpoint_array = [];
    const saveEndpoints = async() => {
      for(let be = 0; be < bulkEndpoints.length; be++){
        let new_e = await Endpoint.create(bulkEndpoints[be],{
          include: [{ model: Endpoint_Property, as: 'properties'},{ model: MFT_Schedule, as: 'schedules'}]
        });
        new_endpoint_array.push(new_e);
      }
      return new_endpoint_array;
    };
    
    saveEndpoints().then(new_endpoint_array => {
      Endpoint.findAll({
        where: {
          bw_process_ident: {[Op.or]: bw_idents}
        }
      }).then(function (bw_id_endpoints) {
        console.log(bw_id_endpoints);
        for(let r = 0; r < bulkRoutes.length; r++){
          for(let i = 0; i < bw_id_endpoints.length; i++){
            if(bulkRoutes[r].producer_id === bw_id_endpoints[i].bw_process_ident){
              bulkRoutes[r].producer_id = bw_id_endpoints[i].id;
            }
            if(bulkRoutes[r].consumer_id === bw_id_endpoints[i].bw_process_ident){
              bulkRoutes[r].consumer_id = bw_id_endpoints[i].id;
            }
          }
        }
        //console.log('344');
        //console.log(bulkRoutes);
        let new_route_array = [];
        const saveRoutes = async() => {
          for(let br = 0; br < bulkRoutes.length; br++){
            let new_r = await Route.create(bulkRoutes[br],{
              include: [{ model: Route_Property, as: 'properties'},{ model: Route_Criteria, as: 'crits'}]
            });
            new_route_array.push(new_r);
          }
          return new_route_array;
        };
        saveRoutes().then(new_route_array => {
          res.redirect('/endpoints');
        });
      });
    });
  });
};

exports.post_export = function (req, res) {
  var MainObj, main_ids = [], where = {}, order, include;
  //console.log(req.body);
  Object.keys(req.body).forEach(function (key) {
    if(key.startsWith("mainitem_")){
      main_ids.push(key.split("_")[1]);
    }
  });
  //console.log(main_ids);
  if(req.body.main_item_type === 'Route'){
    MainObj = Route;
    where = {
      id: { [Op.in]: main_ids }
    };
    order = [['name','ASC']];
    include = [
      {
        model: Endpoint,
        as: 'Producer',
        //where: { producer_id: Sequelize.col('endpoint.id')}
      },
      {
        model: Endpoint,
        as: 'Consumer'
      },
      {
        model: Route_Property,
        as: 'properties'
      },
      {
        model: Route_Criteria,
        as: 'crits'
      }
    ];
  }
  if(req.body.main_item_type === 'Endpoint'){
    MainObj = Endpoint;
    where = {
      id: { [Op.in]: main_ids }
    };
    order = [['name','ASC']];
    include = [
      {
        model: Route,
        as: 'producer_routes',
        //where: { producer_id: Sequelize.col('endpoint.id')}
      },
      {
        model: Route,
        as: 'consumer_routes',
        //where: { producer_id: Sequelize.col('endpoint.id')}
      },
      {
        model: Endpoint_Property,
        as: 'properties'
      },
      {
        model: MFT_Schedule,
        as: 'schedules'
      }
    ];
  }
  MainObj.findAll({
    include: include,
    order: order,
    where: where
  }).then( function (main_items) {
    console.log(main_items[0]);
    res.render('migrate_export_details', {
      main_items: main_items,
      main_item_type: req.body.main_item_type,
      action: req.body.action,
    });
  });
  
};

exports.post = function (req, res) {
  var MainObj, MainType, where = {}, order;
  //console.log(req.body.action);
  if(req.body.action === 'Export'){
    //doing export so lets get main item type and then get that list
    //console.log(req.body.primary_export_item);
    if(req.body.primary_export_item === 'Route'){
      MainObj = Route;
      MainType = 'Route';
      if(req.body.route_type !== 'All'){
        where['type'] = req.body.route_type
      }
      order = [['name','ASC']];
    }
    if(req.body.primary_export_item === 'Endpoint'){
      MainObj = Endpoint;
      MainType = 'Endpoint';
      if(req.body.endpoint_type !== 'All'){
        where['type'] = req.body.endpoint_type
      }
      order = [['name','ASC']];
    }
    if(req.body.active !== 'All'){
      where['active'] = (req.body.active === 'True');
    }
    MainObj.findAll({
      where: where,
      order: order
    }).then(function (main_items) {
      res.render('migrate_export', {
        main_items: main_items,
        main_item_type: MainType,
        action: req.body.action,
      });
    });
    
  }
  else{
    //doing import so read the file
    let i_file = req.files.import_file;
    let ftstamp = moment().format('YYYY-MM-DD-HH-mm-ss');
    i_file.path = './migration/imports/' + ftstamp + '.json.txt';
    i_file.mv(i_file.path, function (err) {
      if (err) throw err;
      fs.readFile(i_file.path, (err, data) => {
        if (err) throw err;
        let importObj = JSON.parse(data);
        console.log(importObj);
        Endpoint.findAll({
          where: {
            'direction': 'producer'
          }
        }).then(function (producers) {
          Endpoint.findAll({
            where: {
              'direction': 'consumer'
            }
          }).then(function (consumers) {
            //make array of idents to check conflicts against
            let e_idents = consumers.map(({bw_process_ident}) => bw_process_ident);
            e_idents = e_idents.concat(producers.map(({bw_process_ident}) => bw_process_ident));
            //i_new_idents = [];
            importObj.endpoints.forEach(function (e) {
              let orig_ident = e.bw_process_ident;
              let index_ident = 1;
              while (e_idents.indexOf(e.bw_process_ident) > -1){
                e.bw_process_ident = orig_ident + '-IMPORT-' + index_ident;
                index_ident++;
              } 
            });
            res.render('migrate_import', {
              import_data: importObj,
              producers: producers,
              consumers: consumers,
              import_file: i_file.path
            });
          });
        });
        
      });
    });
    
    
  }
};

