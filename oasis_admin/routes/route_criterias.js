var express = require('express');
var router = express.Router();
var lg = require('./logcheck.js')

//controllers
var route_criterias_controller = require('../controllers/route_criteriasController');
const Sequelize = require('sequelize');

/* GET home page. */
router.get('/', lg.isLoggedIn, route_criterias_controller.index);
router.get('/view', lg.isLoggedIn, route_criterias_controller.get_view);
router.get('/edit', lg.isLoggedIn, route_criterias_controller.get_edit);
router.get('/add', lg.isLoggedIn, route_criterias_controller.get_create);
router.get('/del', lg.isLoggedIn, route_criterias_controller.get_delete);
router.post('/add', lg.isLoggedIn, route_criterias_controller.post_create);
router.post('/edit', lg.isLoggedIn, route_criterias_controller.post_edit);
/*


router.get('/add_many', lg.isLoggedIn, route_controller.get_create_many);
router.post('/add_many', lg.isLoggedIn, route_controller.post_create_many);


router.post('/edit', lg.isLoggedIn, route_controller.post_edit);*/

module.exports = router;
