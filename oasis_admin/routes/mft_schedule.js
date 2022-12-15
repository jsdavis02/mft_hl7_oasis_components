var express = require('express');
var router = express.Router();
var lg = require('./logcheck.js');

//controllers
var mft_schedule_controller = require('../controllers/mft_scheduleController');


/* GET home page. */
router.get('/', lg.isLoggedIn, mft_schedule_controller.index);

router.get('/add', lg.isLoggedIn, mft_schedule_controller.get_create);

router.post('/add', lg.isLoggedIn, mft_schedule_controller.post_create);

router.get('/view', lg.isLoggedIn, mft_schedule_controller.get_view);

router.get('/edit', lg.isLoggedIn, mft_schedule_controller.get_edit);

router.post('/edit', lg.isLoggedIn, mft_schedule_controller.post_edit);

router.get('/remove', lg.isLoggedIn, mft_schedule_controller.get_remove);

router.get('/toggle_scheduler', lg.isLoggedIn, mft_schedule_controller.toggle_scheduler);

module.exports = router;
