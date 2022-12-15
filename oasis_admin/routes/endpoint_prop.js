var express = require('express');
var router = express.Router();
var lg = require('./logcheck.js')

//controllers
var endpoint_props_controller = require('../controllers/endpoint_propsController');

/* GET home page. */
router.get('/', lg.isLoggedIn, endpoint_props_controller.index);
router.get('/view', lg.isLoggedIn, endpoint_props_controller.get_view);
router.get('/view_decrypt', lg.isLoggedIn, endpoint_props_controller.get_view_decrypted);
router.get('/edit', lg.isLoggedIn, endpoint_props_controller.get_edit);
router.get('/add', lg.isLoggedIn, endpoint_props_controller.get_create);
router.get('/del', lg.isLoggedIn, endpoint_props_controller.get_delete);
router.post('/add', lg.isLoggedIn, endpoint_props_controller.post_create);
router.post('/edit', lg.isLoggedIn, endpoint_props_controller.post_edit);
module.exports = router;
