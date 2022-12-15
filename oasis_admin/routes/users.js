var express = require('express');
var router = express.Router();
var lg = require('./logcheck.js');

var user_controller = require('../controllers/userController');

//analyst views
router.get('/analyst', lg.isLoggedInAnalyst, user_controller.analyst_get_edit);
router.post('/analyst', lg.isLoggedInAnalyst, user_controller.analyst_post_edit);


/* admin views */
router.post('/add_endpoint', lg.isLoggedIn, user_controller.post_user_endpoint_add);

router.get('/', lg.isLoggedIn, user_controller.index);

router.get('/email_invite', lg.isLoggedIn, user_controller.get_email_invite);

router.get('/add', lg.isLoggedIn, user_controller.get_create);

router.post('/add', lg.isLoggedIn, user_controller.post_create);

router.get('/edit', lg.isLoggedIn, user_controller.get_edit);

router.post('/edit', lg.isLoggedIn, user_controller.post_edit);

router.get('/delete', lg.isLoggedIn, user_controller.get_delete);

module.exports = router;

