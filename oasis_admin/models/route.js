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

// setup User model and its fields.
const Route = sequelize.define('route', {
    
    id: {
        type: Sequelize.BIGINT,
        autoIncrement: true,
        primaryKey: true
    },
    active: {
        type: Sequelize.BOOLEAN,
        allowNull: false
    },
    type: {
        type: Sequelize.STRING,
        allowNull: false
    },
    name: {
        type: Sequelize.STRING,
        allowNull: true
    },
    description: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: true
    },
    producer_id: {
        type: Sequelize.BIGINT,
        unique: false,
        allowNull: false
    },
    consumer_id: {
        type: Sequelize.BIGINT,
        unique: false,
        allowNull: false
    },
    producer_messagetypemessagecode: {
        type: Sequelize.STRING,
        allowNull: false
    },
    producer_messagetypetriggerevent: {
        type: Sequelize.STRING,
        allowNull: false
    },
    consumer_messagetypemessagecode: {
        type: Sequelize.STRING,
        allowNull: false
    },
    consumer_messagetypetriggerevent: {
        type: Sequelize.STRING,
        allowNull: false
    },
    hasTranslation: {
        type: Sequelize.BOOLEAN,
        allowNull: false
    },
    hasCriteria: {
        type: Sequelize.BOOLEAN,
        allowNull: false
    },
    hasSplit: {
        type: Sequelize.BOOLEAN,
        allowNull: false
    }
}, {
    timestamps: false,
    freezeTableName: true,
    tableName: 'routes'
});
const Endpoint = require('./endpoint');
/*Route.belongsTo(Endpoint,{
  foreignKey: 'producer_id',
  as: 'Producer'
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
});*/

// create all the defined tables in the specified database.
sequelize.sync()
    .then(() => console.log('route table has been successfully created, if one doesn\'t exist'))
    .catch(error => console.log('This error occured', error));

// export User model for use in other files.
module.exports = Route;