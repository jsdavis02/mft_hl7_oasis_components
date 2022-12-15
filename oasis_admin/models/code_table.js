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

const Code_Table = sequelize.define('code_table', {
    id: {
        type: Sequelize.BIGINT,
        autoIncrement: true,
        primaryKey: true
    },
    input: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: true
    },
    output: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: true
    },
    lookup_key: {
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
    tableName: 'code_table',
});
// create all the defined tables in the specified database.
sequelize.sync()
    .then(() => console.log('code_table table has been successfully created, if one doesn\'t exist'))
    .catch(error => console.log('This error occurred', error));

// export User model for use in other files.
module.exports = Code_Table;