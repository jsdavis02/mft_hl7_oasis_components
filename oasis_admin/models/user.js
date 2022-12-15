var env = process.env.NODE_ENV || 'development';
var config = require('../config/config')[env];
const bcrypt = require('bcrypt-nodejs');
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
    dialectOptions: {
        useUTC: false
    }
});
const Endpoint = require('./endpoint');
// setup User model and its fields.
const User = sequelize.define('user', {
    username: {
        type: Sequelize.STRING,
        unique: true,
        allowNull: false
    },
    email: {
        type: Sequelize.STRING,
        unique: true,
        allowNull: false
    },
    password: {
        type: Sequelize.STRING,
        allowNull: false
    },
    role: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: true
    }
}, {
    freezeTableName: true,
    tableName: 'users',
    /*
    interfering with edit vs create so hashing in usercontroller instead of model.
    hooks: {
        beforeCreate: (user) => {
            const salt = bcrypt.genSaltSync();
            user.password = bcrypt.hashSync(user.password, salt);
        },
        beforeSave: (user) => {
            const salt = bcrypt.genSaltSync();
            if(user.password){
                user.password = bcrypt.hashSync(user.password, salt);
            }
        }
    }*/
});

Endpoint.belongsToMany(User, {through: 'UserEndpoint'});
User.belongsToMany(Endpoint, {through: 'UserEndpoint'});

User.prototype.validPassword = function(password) {
    return bcrypt.compareSync(password, this.password);
}

// create all the defined tables in the specified database.
sequelize.sync()
    .then(() => console.log('users table has been successfully created, if one doesn\'t exist'))
    .catch(error => console.log('This error occured', error));

// export User model for use in other files.
module.exports = User;