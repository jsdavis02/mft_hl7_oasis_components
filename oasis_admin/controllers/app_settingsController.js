let All_Models = require('../models/all_models');
let constants = require('../config/constants');


exports.index = function (req, res) {
    All_Models.App_Setting.findAll({order: [['name','ASC']] }).then(function (app_settings) {
        res.render('app_settings', {
            app_settings: app_settings //send map by guid for output loop
        });
    });
};


exports.get_view = function (req, res) {
    All_Models.App_Setting.findByPk(req.query.id).then(function (app_setting) {
            if (app_setting.name.includes("password") || app_setting.name.includes("passphrase")){
                app_setting.value = "*****";
            }
            res.render('app_setting_view',  {
                app_setting: app_setting
       }); 
    });
};

exports.get_edit = function (req, res) {
    All_Models.App_Setting.findByPk(req.query.id).then(function (app_setting) {
        res.render('app_setting_edit', {
            app_setting: app_setting,
            env_list: constants.env_list
        });
    });
};

exports.get_create = function (req, res) {
    res.render('app_setting_add', {
        env_list: constants.env_list
    });
};

exports.post_create = function (req, res) {
    req.body.name = req.body.name.trim();
    req.body.value = req.body.value.trim();
    All_Models.App_Setting.create(req.body).then(app_setting => {
        res.redirect('/app_settings');
    });
};


exports.post_edit = function (req, res) {
    All_Models.App_Setting.findByPk(req.body.id, {
        
    }).then(function (app_setting) {
        req.body.name = req.body.name.trim();
        req.body.value = req.body.value.trim();
        app_setting.update(req.body).then(function (app_setting) {
            //lets go back to the Endpoint View that includes props
            //instead of the endpoint props view here
            res.redirect('/app_settings');
        });
    });
};

exports.get_copy = function (req, res) {
    All_Models.App_Setting.findByPk(req.query.id).then(function (app_setting) {
        
      All_Models.App_Setting.create(
          {
            name: app_setting.name,
            value: app_setting.value,
            env: app_setting.env
          }
      ).then(app_setting_new => {
            res.redirect('/app_settings/edit?id='+app_setting_new.id); 
      });
    });
};


exports.get_delete = function (req, res) {
  All_Models.App_Setting.findByPk(req.query.id, {}).then(function (app_setting) {
    //let endpoint_id = endpoint_prop.endpoint_id;
    app_setting.destroy().then(app_setting => {
      res.redirect('/app_settings');
    })
  });
};
