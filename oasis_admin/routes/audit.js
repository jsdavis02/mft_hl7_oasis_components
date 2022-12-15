var express = require('express');
var router = express.Router();
var audit_controller = require('../controllers/auditController');
var lg = require('./logcheck.js');

/* GET home page. */
router.get('/', lg.isLoggedIn, audit_controller.index);

router.get('/analyst', lg.isLoggedInAnalyst, audit_controller.analyst);
router.get('/analyst_view', lg.isLoggedInAnalyst, audit_controller.analyst_get_view);
router.get('/analyst_file', lg.isLoggedInAnalyst, audit_controller.analyst_get_audit_file);
router.get('/analyst_error_email', lg.isLoggedInAnalyst, audit_controller.analyst_error_email);

router.get('/file', lg.isLoggedIn, audit_controller.get_audit_file);
router.get('/view', lg.isLoggedIn, audit_controller.get_view);

router.get('/resend', lg.isLoggedIn, audit_controller.get_resend);

router.post('/resend', lg.isLoggedIn, audit_controller.get_resend);

router.get('/reprocess', lg.isLoggedIn, audit_controller.get_reprocess);

router.post('/reprocess', lg.isLoggedIn, audit_controller.get_reprocess);

router.get('/payload_edit', lg.isLoggedIn, audit_controller.get_payload);

router.post('/payload_edit', lg.isLoggedIn, audit_controller.post_payload);

//router.post('/search', lg.isLoggedIn, audit_controller.post_search);

module.exports = router;
