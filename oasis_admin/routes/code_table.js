var express = require('express');
var router = express.Router();
var lg = require('./logcheck.js');

//controllers
var code_table_controller = require('../controllers/code_tableController');


/* GET home page. */
router.get('/', lg.isLoggedIn, code_table_controller.index);
router.get('/add', lg.isLoggedIn, code_table_controller.get_create);
router.post('/add', lg.isLoggedIn, code_table_controller.post_create);
router.get('/upload_csv', lg.isLoggedIn, code_table_controller.get_upload);
router.post('/upload_csv', lg.isLoggedIn, code_table_controller.post_upload);
/*
router.get('/add_many', lg.isLoggedIn, code_table_controller.get_create_many);
router.post('/add_many', lg.isLoggedIn, code_table_controller.post_create_many);
*/
router.get('/view', lg.isLoggedIn, code_table_controller.get_view);
router.get('/edit', lg.isLoggedIn, code_table_controller.get_edit);
router.post('/edit', lg.isLoggedIn, code_table_controller.post_edit);

module.exports = router;
