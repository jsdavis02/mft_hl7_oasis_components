var env = process.env.NODE_ENV || 'development';
var config = require('../config/config')[env];
const constants = require('../config/constants');
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
const Endpoint = sequelize.define('endpoint', {
    id: {
        type: Sequelize.BIGINT,
        autoIncrement: true,
        primaryKey: true
    },
    type: {
        type: Sequelize.STRING,
        unique: true,
        allowNull: false
    },
    bw_process_ident: {
        type: Sequelize.STRING,
        unique: true,
        allowNull: true
    },
    active: {
        type: Sequelize.BOOLEAN,
        allowNull: false
    },
    name: {
        type: Sequelize.STRING,
        unique: true,
        allowNull: true
    },
    organization: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: true
    },
    receiving_app: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: true
    },
    receiving_facility: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: true
    },
    description: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: true
    },
    software: {
        type: Sequelize.STRING,
        allowNull: true
    },
    direction: {
        type: Sequelize.STRING,
        allowNull: false
    },
    doclink: {
        type: Sequelize.STRING,
        allowNull: true
    },
    subsystem: {
        type: Sequelize.STRING,
        allowNull: true
    },
    alert_level: {
        type: Sequelize.INTEGER,
        allowNull: true
    }
}, {
    timestamps: false,
    freezeTableName: true,
    tableName: 'endpoints'
});

Endpoint.orderByType = function(endpoints) {
    let endpoints_by_type = {};
    for(let et of constants.endpoint_types){
        endpoints_by_type[et] = [];
    }
    //console.log(endpoints_by_type);
    for(let e of endpoints){
        endpoints_by_type[e.type].push(e);
    }
    
    return endpoints_by_type;
};

// create all the defined tables in the specified database.
sequelize.sync()
    .then(() => console.log('endpoint table has been successfully created, if one doesn\'t exist'))
    .catch(error => console.log('This error occurred', error));

// export User model for use in other files.
module.exports = Endpoint;