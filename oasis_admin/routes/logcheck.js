module.exports = {
    isLoggedIn(req, res, next)
    {
        
        //console.log("doing loggedin check")
        //console.log(req.isAuthenticated())
        if (req.isAuthenticated()) {
            //console.log(req.user.role);
            //console.log('authenticated')
            if (req.user.role === 'admin'){
                return next();
            }
            
        }
        
        req.session.returnTo = req.baseUrl + req.url;
        res.redirect('/auth/login');
    },
    isLoggedInAnalyst(req, res, next)
    {

        //console.log("doing loggedin check")
        //console.log(req.isAuthenticated())
        if (req.isAuthenticated()) {
            //console.log(req.user.role);
            //console.log('authenticated')
            if (req.user.role === 'admin' || req.user.role === 'analyst'){
                return next();
            }

        }

        req.session.returnTo = req.baseUrl + req.url;
        res.redirect('/auth/login');
    }
};