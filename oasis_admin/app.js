var createError = require('http-errors');
var express = require('express');
var passport = require('passport');
var path = require('path');
var bodyParser = require('body-parser');
var cookieParser = require('cookie-parser');
var session = require('express-session');
var flash = require('connect-flash');
var logger = require('morgan');
//var User = require('./models/user');
var env = process.env.NODE_ENV || 'development';
//var config = require('./config/config')[env];


//var models = require('./models');

var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');
var auditRouter = require('./routes/audit');
var routeRouter = require('./routes/route');
var routePropertyRouter = require('./routes/route_props');
var auditPropertyRouter = require('./routes/audit_props');
var routeCriteriaRouter = require('./routes/route_criterias');
var endpointRouter = require('./routes/endpoint');
var endpointPropertyRouter = require('./routes/endpoint_prop');
var authRouter = require('./routes/auth');
var mft_scheduleRouter = require('./routes/mft_schedule');
var code_tableRouter = require('./routes/code_table');
var migrateRouter = require('./routes/migrate');
var appSettingsRouter = require('./routes/app_settings');
var intRequestsRouter = require('./routes/int_request');
var app = express();
const fileupload = require('express-fileupload');
let hour = 3600000;
//var router = express.Router();
// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

app.use(logger('dev'));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));
app.use(session({
  secret: 'asdfdgewrwe5y565uen',
  resave: false,
  saveUninitialized: false,
  cookie: {
    expires: new Date(Date.now() + hour),
    maxAge: 100 * hour
  }
}));
app.use(flash());
require('./config/passport')(passport);
app.use(passport.initialize());
app.use(passport.session());
app.use(fileupload());

app.use('/', indexRouter);
app.use('/users', usersRouter);
app.use('/audit', auditRouter);
app.use('/routes', routeRouter);
app.use('/route_props', routePropertyRouter);
app.use('/audit_props', auditPropertyRouter);
app.use('/route_criterias', routeCriteriaRouter);
app.use('/endpoints', endpointRouter);
app.use('/endpoint_props', endpointPropertyRouter);
app.use('/auth', authRouter);
app.use('/mft_schedules', mft_scheduleRouter);
app.use('/code_tables', code_tableRouter);
app.use('/migrate', migrateRouter);
app.use('/app_settings', appSettingsRouter);
app.use('/requests', intRequestsRouter);



// catch 404 and forward to error handler

app.use(function (req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});


module.exports = app;


