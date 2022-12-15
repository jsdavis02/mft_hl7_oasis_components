
const User = require('./user');
const Endpoint = require('./endpoint');
const App_Setting = require('./app_settings');
const Audit = require('./audit');
const Code_Table = require('./code_table');
const Endpoint_Property = require('./endpoint_props');
const Int_Request = require('./int_request');
const Int_Request_Property = require('./int_request_props');
const MFT_Schedule = require('./mft_schedule');
const Route = require('./route');
const Route_Criteria = require('./route_criterias');
const Route_Property = require('./route_props');
const Audit_Property = require('./audit_props');

//Associations
User.belongsToMany(Endpoint, {through: 'UserEndpoint'});
Endpoint.belongsToMany(User, {through: 'UserEndpoint'});
Route_Criteria.belongsTo(Route, {
  foreignKey: 'route_id',
  as: 'Route'
});
Route.hasMany(Route_Criteria, {
  foreignKey: 'route_id',
  as: 'crits'
});
Route_Property.belongsTo(Route, {
  foreignKey: 'route_id',
  as: 'Route'
});
Route.hasMany(Route_Property, {
  foreignKey: 'route_id',
  as: 'properties'
});
Route.belongsTo(Endpoint,{
  foreignKey: 'producer_id',
  as: 'Producer'
});
Audit_Property.belongsTo(Audit, {
  foreignKey: 'audit_id',
  as: 'Audit'
});
Audit.hasMany(Audit_Property, {
  foreignKey: 'audit_id',
  as: 'properties'
});
Route.belongsTo(Endpoint,{
  foreignKey: 'consumer_id',
  as: 'Consumer'
});
Endpoint.hasMany(Route, {
  foreignKey: 'producer_id',
  as: 'producer_routes'
});
Endpoint.hasMany(Route, {
  foreignKey: 'consumer_id',
  as: 'consumer_routes'
});
MFT_Schedule.belongsTo(Endpoint, {
  foreignKey: 'endpoint_id',
  as: 'Endpoint'
});
Endpoint.hasMany(MFT_Schedule, {
  foreignKey: 'endpoint_id',
  as: 'schedules'
});
Int_Request_Property.belongsTo(Int_Request, {
  foreignKey: 'int_request_id',
  as: 'IntRequest'
});
Int_Request.hasMany(Int_Request_Property, {
  foreignKey: 'int_request_id',
  as: 'properties'
});
Endpoint_Property.belongsTo(Endpoint, {
  foreignKey: 'endpoint_id',
  as: 'Endpoint'
});
Endpoint.hasMany(Endpoint_Property, {
  foreignKey: 'endpoint_id',
  as: 'properties'
});

module.exports = {
  User: User,
  Endpoint: Endpoint,
  App_Setting: App_Setting,
  Audit: Audit,
  Code_Table: Code_Table,
  Endpoint_Property: Endpoint_Property,
  Int_Request: Int_Request,
  Int_Request_Property: Int_Request_Property,
  MFT_Schedule: MFT_Schedule,
  Route: Route,
  Route_Criteria: Route_Criteria,
  Route_Property: Route_Property,
  Audit_Property: Audit_Property
};
