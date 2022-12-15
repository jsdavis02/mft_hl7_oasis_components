var express = require('express');
var router = express.Router();
var lg = require('./logcheck.js')

//controllers
var endpoint_controller = require('../controllers/endpointController');

/* GET home page. */
//analyst views
router.get('/analyst', lg.isLoggedInAnalyst, endpoint_controller.analyst);
router.get('/analyst_app_restart', lg.isLoggedInAnalyst, endpoint_controller.analyst_get_app_restart);
router.get('/analyst_view', lg.isLoggedInAnalyst, endpoint_controller.analyst_get_view);

//admin views
router.get('/', lg.isLoggedIn, endpoint_controller.index);

router.get('/add', lg.isLoggedIn, endpoint_controller.get_create);

router.post('/add', lg.isLoggedIn, endpoint_controller.post_create);

router.get('/view', lg.isLoggedInAnalyst, endpoint_controller.get_view);

router.get('/edit', lg.isLoggedIn, endpoint_controller.get_edit);

router.post('/edit', lg.isLoggedIn, endpoint_controller.post_edit);

router.post('/search', lg.isLoggedIn, endpoint_controller.post_search);

router.post('/analyst_search', lg.isLoggedInAnalyst, endpoint_controller.analyst_post_search);

router.get('/duplicate', lg.isLoggedIn, endpoint_controller.get_duplicate);

router.post('/duplicate', lg.isLoggedIn, endpoint_controller.post_duplicate);

router.get('/del', lg.isLoggedIn, endpoint_controller.get_delete);

router.get('/app_restart', lg.isLoggedIn, endpoint_controller.get_app_restart);

//open view for requests
router.get('/mft_request', endpoint_controller.get_mft_request);
router.post('/mft_request', endpoint_controller.post_mft_request);

module.exports = router;
