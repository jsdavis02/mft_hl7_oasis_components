var express = require('express');
var router = express.Router();
var lg = require('./logcheck.js')

//controllers
var app_settings_controller = require('../controllers/app_settingsController');
const Sequelize = require('sequelize');

/* GET home page. */
router.get('/', lg.isLoggedIn, app_settings_controller.index);
router.get('/view', lg.isLoggedIn, app_settings_controller.get_view);
router.get('/edit', lg.isLoggedIn, app_settings_controller.get_edit);
router.get('/add', lg.isLoggedIn, app_settings_controller.get_create);
router.get('/del', lg.isLoggedIn, app_settings_controller.get_delete);
router.post('/add', lg.isLoggedIn, app_settings_controller.post_create);
router.post('/edit', lg.isLoggedIn, app_settings_controller.post_edit);
router.get('/copy', lg.isLoggedIn, app_settings_controller.get_copy);

/*


router.get('/add_many', lg.isLoggedIn, route_controller.get_create_many);
router.post('/add_many', lg.isLoggedIn, route_controller.post_create_many);
*/



module.exports = router;
