var express = require('express');
var router = express.Router();
var lg = require('./logcheck.js');

//controllers
var int_request_controller = require('../controllers/int_requestController');

router.get('/', lg.isLoggedIn, int_request_controller.index);
router.get('/view', lg.isLoggedIn, int_request_controller.get_view);
router.get('/edit', lg.isLoggedIn, int_request_controller.get_edit);
router.post('/edit', lg.isLoggedIn, int_request_controller.post_edit);
router.get('/del', lg.isLoggedIn, int_request_controller.get_delete);
//open view for requests
router.get('/add', int_request_controller.get_int_request);
router.post('/add', int_request_controller.post_int_request);

module.exports = router;
