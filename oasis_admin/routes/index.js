var express = require('express');
var router = express.Router();
var lg = require('./logcheck.js')

//controllers
var dash_controller = require('../controllers/dashboardController');
/* GET home page. */
router.get('/', function(req, res, next) {
  if(req.user) {
    if (req.user.role === 'admin') {
      return res.redirect('/admin');
    } else if (req.user.role === 'analyst') {
      return res.redirect('/analyst');
    }
  }
  return res.redirect('/auth/login');
});

router.get('/admin', lg.isLoggedIn, dash_controller.admin_dash);

router.get('/analyst', lg.isLoggedInAnalyst, dash_controller.analyst_dash);

module.exports = router;
