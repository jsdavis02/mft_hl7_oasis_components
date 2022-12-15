var env = process.env.NODE_ENV || 'development';
var config = require('../config/config')[env];
let All_Models = require('../models/all_models');
const csv = require('csvtojson');
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
  for (const qk in req.query) {
    for (const key in All_Models.Code_Table.rawAttributes) {
      if (qk === key) {
        where[key] = req.query[qk]
      }
    }
  }
  All_Models.Code_Table.findAll({
    where: where
  }).then(function (code_tables) {
    sequelize.query('select distinct lookup_key from code_table', {
      model: All_Models.Code_Table,
      mapToModel: true // pass true here if you have any mapped fields
    })
        .then(code_table_keys => {
          res.render('code_table', {
            code_tables: code_tables, //send map by guid for output loop
            wparms: where,
            code_table_keys: code_table_keys
          });
        });
  });
};

exports.get_upload = function (req, res) {
  res.render('upload_csv')
  };

exports.post_upload = function (req, res) {
  console.log(req.files);
  let c_file = req.files.csv_file;
  c_file.path = ('./csv_uploads/' + c_file.name);
  c_file.mv(c_file.path);
  
  csv()
      .fromFile(c_file.path)
      .then((jsonObj) => {
        console.log(jsonObj);
            
  All_Models.Code_Table.bulkCreate(jsonObj).then(function () {
    res.redirect('/code_tables');
    });
  });
};

exports.get_create = function (req, res) {
  sequelize.query('select distinct lookup_key from code_table', {
    model: All_Models.Code_Table,
    mapToModel: true // pass true here if you have any mapped fields
  }).then(code_table_keys => {
      //console.log(code_table_keys);  
      res.render('code_table_add', {
        code_table_keys: code_table_keys
        });
      });
    };

exports.post_create = function (req, res) {
  req.body.lookup_key = (req.body.lookup_key === 'Add New') ? req.body.new_key : req.body.lookup_key;
  All_Models.Code_Table.create(req.body).then(code_table => { 
    res.redirect('/code_tables')});
};

exports.get_edit = function (req, res) {
  All_Models.Code_Table.findByPk(req.query.id, {
  }).then(function (code_table) {
    sequelize.query('select distinct lookup_key from code_table', {
      model: All_Models.Code_Table,
      mapToModel: true // pass true here if you have any mapped fields
    }).then(code_table_keys => {
      //console.log(code_table_keys);  
      res.render('code_table_edit', {
        code_table_keys: code_table_keys,
        code_table: code_table
      });
    });
   });
};

exports.post_edit = function (req, res) {
  req.body.lookup_key = (req.body.lookup_key === 'New') ? req.body.new_key : req.body.lookup_key;
  All_Models.Code_Table.findByPk(req.body.id, {
  }).then(function (code_table) {
    code_table.update(req.body).then(function (code_table) {
      res.redirect('/code_tables');
    });
  });
};

exports.get_view = function (req, res) {
  All_Models.Code_Table.findByPk(req.query.id).then(function (code_table) {
    res.render('code_table_view',{
       code_table: code_table
    });
  })
};
