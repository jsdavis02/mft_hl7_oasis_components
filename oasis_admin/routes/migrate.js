var express = require('express');
var router = express.Router();
var lg = require('./logcheck.js');

//controllers
var migrate_controller = require('../controllers/migrateController');
//const Sequelize = require('sequelize');

/* GET home page. */
router.get('/', lg.isLoggedIn, migrate_controller.index);
router.post('/migrate_export', lg.isLoggedIn, migrate_controller.post);
router.post('/migrate_export_2', lg.isLoggedIn, migrate_controller.post_export)
router.post('/migrate_export_3', lg.isLoggedIn, migrate_controller.post_export_file_gen);
router.post('/migrate_import', lg.isLoggedIn, migrate_controller.post_import);
/*
router.get('/add', lg.isLoggedIn, route_controller.get_create);

router.post('/add', lg.isLoggedIn, route_controller.post_create);

router.get('/add_many', lg.isLoggedIn, route_controller.get_create_many);

router.post('/add_many', lg.isLoggedIn, route_controller.post_create_many);
//todo make an analyst specific view
router.get('/view', lg.isLoggedInAnalyst, route_controller.get_view);
router.get('/edit', lg.isLoggedIn, route_controller.get_edit);
router.post('/edit', lg.isLoggedIn, route_controller.post_edit);
router.get('/del', lg.isLoggedIn, route_controller.get_delete);
router.post('/search', lg.isLoggedIn, route_controller.post_search);*/

module.exports = router;
