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

const IntRequest = sequelize.define('int_request', {
    id: {
        type: Sequelize.BIGINT,
        autoIncrement: true,
        primaryKey: true
    },
    status: {
        type: Sequelize.STRING,
        unique: false,
    },
    contact_name: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: false
    },
    contact_email: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: false
    },
    contact_phone: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: true
    },
    description: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: true
    },
    producer_description: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: true
    },
    consumer_description: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: true
    },
    producer_type: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: false
    },
    consumer_type: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: false
    },
    data_transfer_req: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: true
    },
    data_manipulation_req: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: true
    },
    doclink: {
        type: Sequelize.STRING,
        allowNull: true
    }
}, {
    timestamps: false,
    freezeTableName: true,
    tableName: 'int_requests',
    useUTC: false
});



// create all the defined tables in the specified database.
sequelize.sync()
    .then(() => console.log('int_requests table has been successfully created, if one doesn\'t exist'))
    .catch(error => console.log('This error occurred', error));

// export User model for use in other files.
module.exports = IntRequest;