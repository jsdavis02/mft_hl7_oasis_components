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
    dialectOptions: {
        options: {
            useUTC: false,
            dateFormat: 'YYYY-MM-DD HH:mm:ss',
        },
        fake2: 'bar',
    },
    options: {
        useUTC: false
    },
    timezone: '-07:00'

});
const Endpoint = require('./endpoint');
// setup User model and its fields.
const MFT_Schedule = sequelize.define('mft_schedule', {
    id: {
        type: Sequelize.BIGINT,
        autoIncrement: true,
        primaryKey: true
    },
    active: {
        type: Sequelize.BOOLEAN,
        allowNull: false
    },
    endpoint_id: {
        type: Sequelize.BIGINT,
        unique: false,
        allowNull: false
    },
    name: {
        type: Sequelize.STRING,
        allowNull: true
    },
    freq_type: {
        type: Sequelize.STRING,
        allowNull: false
    },
    freq_interval: {
        type: Sequelize.INTEGER,
        allowNull: true
    },
    sub_freq_interval: {
        type: Sequelize.INTEGER,
        allowNull: true
    },
    spec_date: {
        type: Sequelize.DATEONLY,
        allowNull: true
    },
    spec_time: {
        type: Sequelize.TIME,
        allowNull: true
    },
    last_run: {
        type: Sequelize.DATE,
        allowNull: true,
        dateFormat: 'YYYY-MM-DD HH:mm:ss',
    },
    sub_day_freq_type: {
        type: Sequelize.STRING,
        allowNull: true
    },
    sub_day_freq_interval: {
        type: Sequelize.INTEGER,
        allowNull: true
    },
    sub_day_stop_schedule: {
        type: Sequelize.BOOLEAN,
        allowNull: true
    },
    sub_day_start_time: {
        type: Sequelize.TIME,
        allowNull: true
    },
    sub_day_end_time: {
        type: Sequelize.TIME,
        allowNull: true
    },
    last_files_found: {
        type: Sequelize.DATE,
        allowNull: true
    },
    pause_start: {
        type: Sequelize.DATE,
        allowNull: true,
        dateFormat: 'YYYY-MM-DD HH:mm:ss',
    },
    pause_end: {
        type: Sequelize.DATE,
        allowNull: true,
        dateFormat: 'YYYY-MM-DD HH:mm:ss',
    },
}, {
    timestamps: false,
    freezeTableName: true,
    tableName: 'mft_schedule',
    useUTC: false,
});
MFT_Schedule.prototype.setValuesForDisplay = function(){
    let constants = require('../config/constants');
    let moment = require('moment');
    if(this.freq_type === 'Monthly_Weekly'){
        //change freq_int and sub_freq_int to disp
        let w = constants.weekdays;
        let l = w.find(w => w.value === this.sub_freq_interval);
        this.sub_freq_interval = l.label;
        let mw = constants.monthly_weekly_options;
        this.freq_interval = mw.find(mw => mw.value === this.freq_interval).label;
    }
    if(this.freq_type === 'Weekly'){
        //change freq_int and sub_freq_int to disp
        let w = constants.weekdays;
        let l = w.find(w => w.value === this.freq_interval);
        this.freq_interval = l.label;
        
    }
    if(this.spec_date){
        //console.log(this.spec_date);
        this.spec_date = moment.utc(this.spec_date).format('YYYY-MM-DD');
        //console.log(this.spec_date);
    }
    if(this.spec_time){
        //console.log(this.spec_time)
        this.spec_time = moment.utc(this.spec_time).format('YYYY-MM-DD[T]HH:mm');
        //console.log(this.spec_time)
    }
    if(this.sub_day_start_time){
        this.sub_day_start_time = moment.utc(this.sub_day_start_time).format('YYYY-MM-DD[T]HH:mm');
        //  console.log(this.sub_day_start_time);
    }
    if(this.sub_day_end_time){
        this.sub_day_end_time = moment.utc(this.sub_day_end_time).format('YYYY-MM-DD[T]HH:mm');
    }
    if(this.pause_start){
        //console.log(typeof this.pause_start);
        this.pause_start = moment.utc(this.pause_start).format('YYYY-MM-DD[T]HH:mm');
    }
    if(this.pause_end){
        this.pause_end = moment.utc(this.pause_end).format('YYYY-MM-DD[T]HH:mm');
    }
    if(this.last_run){
        this.last_run = moment.utc(this.last_run).format('YYYY-MM-DD[T]HH:mm');
    }
    if(this.last_files_found){
        this.last_files_found = moment.utc(this.last_files_found).format('YYYY-MM-DD[T]HH:mm');
    }
    return this;
};
/*
MFT_Schedule.belongsTo(Endpoint, {
    foreignKey: 'endpoint_id',
    as: 'Endpoint'
});
Endpoint.hasMany(MFT_Schedule, {
    foreignKey: 'endpoint_id',
    as: 'schedules'
});
*/


// create all the defined tables in the specified database.
sequelize.sync()
    .then(() => console.log('mft_schedule table has been successfully created, if one doesn\'t exist'))
    .catch(error => console.log('This error occurred', error));

// export User model for use in other files.
module.exports = MFT_Schedule;