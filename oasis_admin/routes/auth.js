var express = require('express');
var router = express.Router();

var auth_controller = require('../controllers/authController');

/* GET users listing. */
router.get('/login', auth_controller.get_login);

router.post('/login', auth_controller.post_login);

router.get('/logout', auth_controller.get_logout);

module.exports = router;

function isLoggedIn(req, res, next) {
    if (req.isAuthenticated())
        return next();
    res.redirect('/');
}
