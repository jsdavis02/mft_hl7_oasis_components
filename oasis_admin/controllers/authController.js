
var passport = require('passport');

require('../config/passport');
//var passport = require('../config/passport');

var exports = module.exports = {}

exports.get_logout = function(req, res) {
    req.logout();
    res.redirect('/auth/login');
};

exports.get_login = function (req, res) {
    res.render('login');
};

exports.post_login = function (req, res, next) {
    console.log('in post login');
    console.log(req.session.returnTo);
    passport.authenticate('local-login', (err, user, info) => {
        if(info) {return res.send(info.message)}
        if (err) { return next(err); }
        if (!user) { return res.redirect('/auth/login'); }
        req.login(user, (err) => {
            if (err) { return next(err); }
            if (user.role === 'analyst') { return res.redirect('/audit/analyst'); }
            url = '/audit';
            if (req.session && req.session.returnTo) {
                url = req.session.returnTo;
                delete req.session.returnTo;
            }
            return res.redirect(url);
        })
        //res.redirect('/audit');
    })(req, res, next);
    
    /*passport.authenticate('local', {
        successRedirect: '/endpoints/add',
        failureRedirect: '/auth/login'
    });*/
};

exports.get_signup = function (req, res) {
    
};

exports.post_signup = function (req, res) {
    
};