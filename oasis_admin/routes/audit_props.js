var express = require('express');
var router = express.Router();
var lg = require('./logcheck.js');

//controllers
var route_props_controller = require('../controllers/auditController');
const Sequelize = require('sequelize');

/* GET home page. */
router.get('/', lg.isLoggedIn, route_props_controller.index);
router.get('/view', lg.isLoggedIn, route_props_controller.get_view);

module.exports = router;
