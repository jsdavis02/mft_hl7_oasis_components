//var passport = require('passport');
var LocalStrategy = require('passport-local').Strategy;
var User = require('../models/user');



module.exports = function(passport){

    passport.serializeUser(function(user, done) {
        done(null, user.id);
        return done;
    });
    /*
    passport.deserializeUser(function(id, done) {
        User.findByPk(id).then(function(err, user){
            console.log(user)
            console.log(err)
            done(err, user);
        });
    });
*/
    /*
    //Serialize sessions
    passport.serializeUser(function (user, done) {
        done(null, user.id);
    });
*/
    //deserialize
    passport.deserializeUser(function (user, done) {
       User.findByPk(user).then(function (user) {
          done(null, user); 
          return done;
       }).error(function (err) {
           done(err, null);
           return done;
       }); 
    });
    
    //for auth
    passport.use('local-login',new LocalStrategy({
            usernameField: 'username',
            passwordField: 'password',
            passReqToCallback : true
        },
        function(req, username, password, done) {
            //console.log('in auth function');
            User.findOne({where: {username: username }}).then(function (user) {
                //console.log(user)
                if (!user) { 
                    //console.log('no user')
                    return done(null, false); }
                if (!user.validPassword(password)) { 
                    console.log('password wrong')
                    return done(null, false); }
                return done(null, user);
            });
            
        }
    ));

    
}