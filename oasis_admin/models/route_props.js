var env = process.env.NODE_ENV || 'development';
var config = require('../config/config')[env];
const Sequelize = require('sequelize');
const sequelize = new Sequelize(config.database.db,config.database.user,config.database.pass, {
    host: config.database.host,
    dialect: 'mssql',
    operatorsAliases: false,

    pool: {
        max: 5,
        min: 0,
        acquire: 30000,
        idle: 10000
    },


});
const Route_Property = sequelize.define('route_prop', {
    id: {
        type: Sequelize.BIGINT,
        autoIncrement: true,
        primaryKey: true
    },
    route_id: {
        type: Sequelize.BIGINT,
        allowNull: false
    },
    name: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: false
    },
    value: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: true
    },
    env: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: false
    }
},{
    timestamps: false,
    freezeTableName: true,
    tableName: 'route_props'
});
/*Route_Property.belongsTo(Route, {
    foreignKey: 'route_id',
    as: 'Route'
});
Route.hasMany(Route_Property, {
    foreignKey: 'route_id',
    as: 'properties'
});*/
// create all the defined tables in the specified database.
sequelize.sync()
    .then(() => console.log('route_props table has been successfully created, if one doesn\'t exist'))
    .catch(error => console.log('This error occurred', error));

// export User model for use in other files.
module.exports = Route_Property;