var express = require('express');
var router = express.Router();
var lg = require('./logcheck.js');

//controllers
var route_controller = require('../controllers/routeController');
//const Sequelize = require('sequelize');
//analyst views
router.get('/analyst_route_view', lg.isLoggedInAnalyst, route_controller.get_analyst_view);

/* GET home page. */
router.get('/', lg.isLoggedIn, route_controller.index);

router.get('/add', lg.isLoggedIn, route_controller.get_create);

router.post('/add', lg.isLoggedIn, route_controller.post_create);

router.get('/add_many', lg.isLoggedIn, route_controller.get_create_many);

router.post('/add_many', lg.isLoggedIn, route_controller.post_create_many);
router.get('/view', lg.isLoggedIn, route_controller.get_view);
router.get('/edit', lg.isLoggedIn, route_controller.get_edit);
router.post('/edit', lg.isLoggedIn, route_controller.post_edit);
router.get('/del', lg.isLoggedIn, route_controller.get_delete);
router.post('/search', lg.isLoggedIn, route_controller.post_search);



module.exports = router;
