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
        useUTC: false
    }

});

// setup User model and its fields.
const Audit = sequelize.define('audit', {
    type: {
        type: Sequelize.STRING,
        allowNull: true
    },
    MessageReference: {
        type: Sequelize.STRING,
        allowNull: true
    },
    data_format: {
        type: Sequelize.STRING,
        allowNull: true
    },
    ProcessState: {
        type: Sequelize.STRING,
        unique: false,
        allowNull: false
    },
    MessageGUID: {
        type: Sequelize.BIGINT,
        unique: false,
        allowNull: false
    },
    MessageControlID: {
        type: Sequelize.STRING,
        allowNull: true
    },
    DateTimeofMessage: {
        type: Sequelize.DATE,
        allowNull: true
    },
    proc_time:{
        type: Sequelize.DATE,
        allowNull: true,
        dateFormat: 'YYYY-MM-DD HH:mm:ss',
    },
    MessagePayload:{
        type: Sequelize.TEXT,
        allowNull: true
    },
    producer_ident: {
        type: Sequelize.STRING,
        allowNull: true
    },
    consumer_ident: {
        type: Sequelize.STRING,
        allowNull: true
    },
    route_id: {
        type: Sequelize.BIGINT,
        allowNull: true
    },
    producer_id: {
        type: Sequelize.BIGINT,
        allowNull: true
    },
    consumer_id: {
        type: Sequelize.BIGINT,
        allowNull: true
    },
    description: {
        type: Sequelize.TEXT,
        allowNull: true
    },
    created_at: {
        type: Sequelize.DATE,
        allowNull: true
    },
    modified_at: {
        type: Sequelize.DATE,
        allowNull: true
    }
}, {
    timestamps: false,
    freezeTableName: true,
    tableName: 'audit',
    useUTC: false,
});

Audit.sortArrayByGUID = function(auditarray){
    var nAudits = [];
    var auditMap = new Map();
    var curAuditGuid = '';
    //we depend on the list being in guid order already but just in case
    auditarray = auditarray.sort(function (a,b){
        if(a.MessageGUID < b.MessageGUID){ return -1;}
        if(a.MessageGUID > b.MessageGUID) { return 1;}
        return 0;
    });
    ///console.log(JSON.stringify(auditarray));
    var audit;
    for(var x=0; x<auditarray.length; x++){
        //console.log('Audit Record:' +JSON.stringify(audit)+"\n");
       audit = auditarray[x];
       if(x==0){curAuditGuid = audit.MessageGUID;}
       if (curAuditGuid !== audit.MessageGUID && x > 0) {
           //new message set
           console.log('Audit Array:'+JSON.stringify(nAudits));
           auditMap.set(curAuditGuid,nAudits);
           nAudits = [];
           curAuditGuid = audit.MessageGUID;
           //console.log('Audit Map:'+JSON.stringify(auditMap.get(curAuditGuid)));
       }
       else {
           //just add to array
           nAudits.push(audit);
           console.log('nAudit:'+JSON.stringify(nAudits));
       }
       //console.log(JSON.stringify(nAudits));
    }
    //console.log(JSON.stringify(auditMap));
    var keys = auditMap.keys();
    console.log(keys.next().value);
    var entries = auditMap.entries();
    console.log(entries.next().value);
    return auditMap;
}

// create all the defined tables in the specified database.
sequelize.sync()
    .then(() => console.log('audit table has been successfully created, if one doesn\'t exist'))
    .catch(error => console.log('This error occurred', error));

// export User model for use in other files.
module.exports = Audit;